"""
Airtel Money OpenAPI Integration
Handles payment initiation, callbacks, and transaction verification
"""
import requests
from django.conf import settings
from apps.payments.models import Payment, PaymentCallback
from django.utils import timezone


class AirtelAPI:
    """Airtel Money API client"""
    
    def __init__(self):
        self.client_id = settings.AIRTEL_CLIENT_ID
        self.client_secret = settings.AIRTEL_CLIENT_SECRET
        self.callback_url = settings.AIRTEL_CALLBACK_URL
        
        if settings.AIRTEL_ENVIRONMENT == 'production':
            self.base_url = 'https://openapiuat.airtel.africa'  # Update to production URL
        else:
            self.base_url = 'https://openapiuat.airtel.africa'
    
    def get_access_token(self):
        """Get OAuth access token"""
        url = f"{self.base_url}/auth/oauth2/token"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json().get('access_token')
        
        raise Exception(f"Failed to get access token: {response.text}")
    
    def initiate_payment(self, phone_number, amount, transaction_id):
        """Initiate Airtel Money payment"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/merchant/v1/payments/"
        
        # Format phone number (country code + number)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]  # Kenya code
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-Country': 'KE',  # Country code
            'X-Currency': 'KES'  # Currency
        }
        
        payload = {
            'reference': transaction_id,
            'subscriber': {
                'country': 'KE',
                'currency': 'KES',
                'msisdn': phone_number
            },
            'transaction': {
                'amount': float(amount),
                'country': 'KE',
                'currency': 'KES',
                'id': transaction_id
            }
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def query_transaction(self, transaction_id):
        """Query Airtel Money transaction status"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/standard/v1/payments/{transaction_id}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json',
            'X-Country': 'KE',
            'X-Currency': 'KES'
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


def initiate_airtel_payment(payment: Payment):
    """Initiate Airtel Money payment"""
    try:
        # Check if we're in development mode (no credentials configured)
        if not settings.AIRTEL_CLIENT_ID or not settings.AIRTEL_CLIENT_SECRET:
            # Simulation mode for development/testing
            payment.status = 'processing'
            payment.metadata = {
                'airtel_transaction_id': f'sim_airtel_{payment.transaction_reference}',
                'simulation_mode': True
            }
            payment.save()
            
            # Auto-complete in simulation mode
            from django.utils import timezone
            payment.status = 'success'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update sale
            payment.sale.amount_paid += payment.amount
            payment.sale.update_payment_status()
            payment.sale.save()
            
            return {'success': True, 'payment': payment, 'simulation': True}
        
        # Real Airtel API call
        airtel = AirtelAPI()
        
        result = airtel.initiate_payment(
            phone_number=payment.phone_number,
            amount=payment.amount,
            transaction_id=payment.transaction_reference
        )
        
        if result.get('status', {}).get('code') == '200':
            # Success - update payment
            payment.status = 'processing'
            payment.metadata = {
                'airtel_transaction_id': result.get('data', {}).get('transaction', {}).get('id')
            }
            payment.save()
            
            return {'success': True, 'payment': payment}
        else:
            return {
                'success': False,
                'error': result.get('status', {}).get('message', 'Airtel request failed')
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def process_airtel_callback(callback_data):
    """Process Airtel Money callback/webhook"""
    try:
        transaction_id = callback_data.get('transaction', {}).get('id')
        status_code = callback_data.get('transaction', {}).get('status', {}).get('code')
        
        # Find payment by transaction reference
        payment = Payment.objects.filter(
            transaction_reference=transaction_id
        ).first()
        
        # Create callback record
        callback = PaymentCallback.objects.create(
            payment=payment,
            callback_type='airtel_callback',
            raw_data=callback_data,
            success=(status_code == 'TS')  # TS = Transaction Successful
        )
        
        if status_code == 'TS':
            # Payment successful
            transaction_data = callback_data.get('transaction', {})
            
            callback.transaction_id = transaction_id
            callback.amount = transaction_data.get('amount')
            callback.phone_number = transaction_data.get('msisdn')
            callback.processed = True
            callback.processed_at = timezone.now()
            callback.save()
            
            if payment:
                # Update payment
                payment.status = 'success'
                payment.external_reference = transaction_id
                payment.completed_at = timezone.now()
                payment.save()
                
                # Update sale
                payment.sale.amount_paid += payment.amount
                payment.sale.update_payment_status()
        else:
            # Payment failed
            callback.error_message = callback_data.get('transaction', {}).get('status', {}).get('message', '')
            callback.processed = True
            callback.processed_at = timezone.now()
            callback.save()
            
            if payment:
                payment.status = 'failed'
                payment.error_message = callback.error_message
                payment.save()
        
        return {'success': True}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def verify_airtel_payment(payment: Payment):
    """Verify Airtel Money payment status"""
    try:
        airtel = AirtelAPI()
        result = airtel.query_transaction(payment.transaction_reference)
        
        status_code = result.get('data', {}).get('transaction', {}).get('status', {}).get('code')
        
        if status_code == 'TS':
            payment.status = 'success'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update sale
            payment.sale.amount_paid += payment.amount
            payment.sale.update_payment_status()
        elif status_code in ['TF', 'TD']:  # Failed or Declined
            payment.status = 'failed'
            payment.error_message = result.get('data', {}).get('transaction', {}).get('status', {}).get('message', '')
            payment.save()
        
        return {'success': True, 'payment': payment}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def process_airtel_refund(refund):
    """Process Airtel Money refund"""
    # Airtel refunds may require separate API implementation
    # This is a placeholder
    return {
        'success': False,
        'error': 'Airtel refunds require manual processing or separate API setup'
    }
