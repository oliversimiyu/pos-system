"""
Card Payment Gateway Integration (Pesapal/Flutterwave/Generic)
Handles card payments via payment gateways
"""
import requests
from django.conf import settings
from apps.payments.models import Payment, PaymentCallback
from django.utils import timezone
import hashlib
import hmac


class CardPaymentGateway:
    """Generic Card Payment Gateway client"""
    
    def __init__(self):
        self.api_key = settings.PAYMENT_GATEWAY_API_KEY
        self.secret = settings.PAYMENT_GATEWAY_SECRET
        self.callback_url = settings.PAYMENT_GATEWAY_CALLBACK_URL
        
        # Example base URL - update based on your gateway (Pesapal, Flutterwave, etc.)
        self.base_url = 'https://api.paymentgateway.com'
    
    def generate_signature(self, data):
        """Generate HMAC signature for request"""
        message = ''.join([str(v) for v in data.values()])
        signature = hmac.new(
            self.secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def initiate_payment(self, amount, transaction_id, customer_email='', customer_phone=''):
        """Initiate card payment"""
        url = f"{self.base_url}/v1/payments/initiate"
        
        payload = {
            'api_key': self.api_key,
            'amount': float(amount),
            'currency': 'KES',
            'transaction_id': transaction_id,
            'callback_url': self.callback_url,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'payment_methods': ['card', 'mobile_money']
        }
        
        # Add signature
        payload['signature'] = self.generate_signature(payload)
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()
    
    def verify_payment(self, transaction_id):
        """Verify card payment status"""
        url = f"{self.base_url}/v1/payments/verify/{transaction_id}"
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        return response.json()
    
    def process_refund(self, transaction_id, amount, reason=''):
        """Process card payment refund"""
        url = f"{self.base_url}/v1/refunds/initiate"
        
        payload = {
            'api_key': self.api_key,
            'transaction_id': transaction_id,
            'amount': float(amount),
            'reason': reason
        }
        
        payload['signature'] = self.generate_signature(payload)
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        return response.json()


def initiate_card_payment(payment: Payment):
    """Initiate card payment"""
    try:
        gateway = CardPaymentGateway()
        
        result = gateway.initiate_payment(
            amount=payment.amount,
            transaction_id=payment.transaction_reference,
            customer_email=getattr(payment.sale.cashier, 'email', ''),
            customer_phone=payment.phone_number or payment.sale.customer_phone
        )
        
        if result.get('status') == 'success':
            # Success - update payment
            payment.status = 'processing'
            payment.metadata = {
                'gateway_transaction_id': result.get('data', {}).get('transaction_id'),
                'payment_url': result.get('data', {}).get('payment_url'),
                'redirect_url': result.get('data', {}).get('redirect_url')
            }
            payment.save()
            
            return {
                'success': True,
                'payment': payment,
                'payment_url': result.get('data', {}).get('payment_url')
            }
        else:
            return {
                'success': False,
                'error': result.get('message', 'Gateway request failed')
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def process_card_callback(callback_data):
    """Process card payment callback/webhook"""
    try:
        transaction_id = callback_data.get('transaction_id')
        status = callback_data.get('status')
        
        # Find payment by transaction reference
        payment = Payment.objects.filter(
            transaction_reference=transaction_id
        ).first()
        
        # Create callback record
        callback = PaymentCallback.objects.create(
            payment=payment,
            callback_type='card_callback',
            raw_data=callback_data,
            success=(status == 'success')
        )
        
        if status == 'success':
            # Payment successful
            callback.transaction_id = callback_data.get('gateway_transaction_id', transaction_id)
            callback.amount = callback_data.get('amount')
            callback.processed = True
            callback.processed_at = timezone.now()
            callback.save()
            
            if payment:
                # Update payment
                payment.status = 'success'
                payment.external_reference = callback_data.get('gateway_transaction_id')
                payment.completed_at = timezone.now()
                payment.metadata.update({
                    'card_type': callback_data.get('card_type'),
                    'card_last4': callback_data.get('card_last4')
                })
                payment.save()
                
                # Update sale
                payment.sale.amount_paid += payment.amount
                payment.sale.update_payment_status()
        else:
            # Payment failed
            callback.error_message = callback_data.get('message', 'Payment failed')
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


def verify_card_payment(payment: Payment):
    """Verify card payment status"""
    try:
        gateway = CardPaymentGateway()
        result = gateway.verify_payment(payment.transaction_reference)
        
        if result.get('status') == 'success':
            payment.status = 'success'
            payment.external_reference = result.get('data', {}).get('gateway_transaction_id')
            payment.completed_at = timezone.now()
            payment.save()
            
            # Update sale
            payment.sale.amount_paid += payment.amount
            payment.sale.update_payment_status()
        elif result.get('status') in ['failed', 'declined']:
            payment.status = 'failed'
            payment.error_message = result.get('message', 'Payment failed')
            payment.save()
        
        return {'success': True, 'payment': payment}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def process_card_refund(refund):
    """Process card payment refund"""
    try:
        gateway = CardPaymentGateway()
        
        result = gateway.process_refund(
            transaction_id=refund.payment.external_reference,
            amount=refund.amount,
            reason=refund.reason
        )
        
        if result.get('status') == 'success':
            refund.status = 'completed'
            refund.external_reference = result.get('data', {}).get('refund_id')
            refund.completed_at = timezone.now()
            refund.approved_by = refund.requested_by
            refund.save()
            
            # Update payment status
            refund.payment.status = 'refunded'
            refund.payment.save()
            
            return {'success': True, 'refund': refund}
        else:
            return {
                'success': False,
                'error': result.get('message', 'Refund failed')
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
