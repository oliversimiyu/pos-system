"""
M-Pesa Daraja API Integration
Handles STK Push, callbacks, and transaction verification
"""
import requests
import base64
from datetime import datetime
from django.conf import settings
from apps.payments.models import Payment, PaymentCallback
from django.utils import timezone


class MpesaAPI:
    """M-Pesa Daraja API client"""
    
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL
        
        if settings.MPESA_ENVIRONMENT == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'
    
    def get_access_token(self):
        """Get OAuth access token"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        response = requests.get(
            url,
            auth=(self.consumer_key, self.consumer_secret)
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        
        raise Exception(f"Failed to get access token: {response.text}")
    
    def generate_password(self, timestamp):
        """Generate password for STK push"""
        data_to_encode = f"{self.shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode()).decode('utf-8')
    
    def stk_push(self, phone_number, amount, account_reference, transaction_desc):
        """Initiate STK Push"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = self.generate_password(timestamp)
        
        # Format phone number (remove leading 0, add 254)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.shortcode,
            'PhoneNumber': phone_number,
            'CallBackURL': self.callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        # Handle non-JSON responses
        try:
            return response.json()
        except ValueError:
            # Return error with raw response text
            return {
                'ResponseCode': '1',
                'ResponseDescription': f'Invalid response from M-Pesa: {response.text[:200]}',
                'errorCode': 'INVALID_RESPONSE',
                'errorMessage': response.text
            }
    
    def query_transaction(self, checkout_request_id):
        """Query STK Push transaction status"""
        access_token = self.get_access_token()
        url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = self.generate_password(timestamp)
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()


def initiate_mpesa_payment(payment: Payment):
    """Initiate M-Pesa STK Push payment"""
    try:
        # Check if we're in development mode (no credentials configured)
        if not settings.MPESA_CONSUMER_KEY or not settings.MPESA_CONSUMER_SECRET:
            # Simulation mode for development/testing
            payment.status = 'processing'
            payment.metadata = {
                'checkout_request_id': f'sim_{payment.transaction_reference}',
                'merchant_request_id': f'sim_merchant_{payment.id}',
                'simulation_mode': True
            }
            payment.save()
            
            # Auto-complete after 3 seconds in simulation mode
            from django.utils import timezone
            payment.status = 'success'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update sale - reload to avoid stale data
            sale = payment.sale
            sale.amount_paid += payment.amount
            sale.update_payment_status()  # This already saves
            
            return {'success': True, 'payment': payment, 'simulation': True}
        
        # Real M-Pesa API call
        mpesa = MpesaAPI()
        
        result = mpesa.stk_push(
            phone_number=payment.phone_number,
            amount=payment.amount,
            account_reference=payment.transaction_reference,
            transaction_desc=f"Payment for Sale {payment.sale.sale_number}"
        )
        
        if result.get('ResponseCode') == '0':
            # Success - update payment
            payment.status = 'processing'
            payment.metadata = {
                'checkout_request_id': result.get('CheckoutRequestID'),
                'merchant_request_id': result.get('MerchantRequestID')
            }
            payment.save()
            
            return {'success': True, 'payment': payment}
        else:
            return {
                'success': False,
                'error': result.get('ResponseDescription', 'M-Pesa request failed')
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def process_mpesa_callback(callback_data):
    """Process M-Pesa callback/webhook"""
    try:
        # Extract callback data
        body = callback_data.get('Body', {}).get('stkCallback', {})
        
        merchant_request_id = body.get('MerchantRequestID')
        checkout_request_id = body.get('CheckoutRequestID')
        result_code = body.get('ResultCode')
        result_desc = body.get('ResultDesc')
        
        # Find payment by checkout_request_id
        payment = Payment.objects.filter(
            metadata__checkout_request_id=checkout_request_id
        ).first()
        
        # Create callback record
        callback = PaymentCallback.objects.create(
            payment=payment,
            callback_type='mpesa_callback',
            raw_data=callback_data,
            success=(result_code == 0)
        )
        
        if result_code == 0:
            # Payment successful
            callback_metadata = body.get('CallbackMetadata', {}).get('Item', [])
            
            # Extract transaction details
            transaction_id = None
            amount = None
            phone_number = None
            
            for item in callback_metadata:
                if item.get('Name') == 'MpesaReceiptNumber':
                    transaction_id = item.get('Value')
                elif item.get('Name') == 'Amount':
                    amount = item.get('Value')
                elif item.get('Name') == 'PhoneNumber':
                    phone_number = item.get('Value')
            
            # Update callback
            callback.transaction_id = transaction_id
            callback.amount = amount
            callback.phone_number = phone_number
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
            callback.error_message = result_desc
            callback.processed = True
            callback.processed_at = timezone.now()
            callback.save()
            
            if payment:
                payment.status = 'failed'
                payment.error_message = result_desc
                payment.save()
        
        return {'success': True}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def verify_mpesa_payment(payment: Payment):
    """Verify M-Pesa payment status"""
    try:
        checkout_request_id = payment.metadata.get('checkout_request_id')
        
        if not checkout_request_id:
            return {'success': False, 'error': 'No checkout request ID found'}
        
        mpesa = MpesaAPI()
        result = mpesa.query_transaction(checkout_request_id)
        
        # Check if query failed due to API error
        if result.get('errorCode'):
            # API error (likely IP block) - return current status without changing it
            return {
                'success': True, 
                'payment': payment,
                'note': 'Query blocked, status unchanged. Setup ngrok for callbacks.'
            }
        
        result_code = result.get('ResultCode')
        
        if result_code == '0':
            payment.status = 'success'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update sale
            payment.sale.amount_paid += payment.amount
            payment.sale.update_payment_status()
        elif result_code == '1032':
            # Request cancelled by user
            payment.status = 'cancelled'
            payment.error_message = 'Cancelled by user'
            payment.save()
        elif result_code == '1037':
            # Request timeout (no response from user)
            payment.status = 'failed'
            payment.error_message = 'Request timeout - no user response'
            payment.save()
        else:
            payment.status = 'failed'
            payment.error_message = result.get('ResultDesc', 'Transaction failed')
            payment.save()
        
        return {'success': True, 'payment': payment}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def process_mpesa_refund(refund):
    """Process M-Pesa refund (B2C)"""
    # M-Pesa refunds require B2C API implementation
    # This is a placeholder - implement based on your business requirements
    return {
        'success': False,
        'error': 'M-Pesa refunds require manual processing or B2C API setup'
    }
