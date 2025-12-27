#!/usr/bin/env python
"""
M-Pesa Integration Test Script
Run this to test M-Pesa STK Push without frontend
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_backend.settings')
django.setup()

from payments.mpesa.services import MpesaAPI
from django.conf import settings
import json


def test_credentials():
    """Test if M-Pesa credentials are configured"""
    print("=" * 60)
    print("TESTING M-PESA CREDENTIALS")
    print("=" * 60)
    
    config = {
        'Consumer Key': settings.MPESA_CONSUMER_KEY,
        'Consumer Secret': settings.MPESA_CONSUMER_SECRET[:10] + '...' if settings.MPESA_CONSUMER_SECRET else '',
        'Shortcode': settings.MPESA_SHORTCODE,
        'Passkey': settings.MPESA_PASSKEY[:10] + '...' if settings.MPESA_PASSKEY else '',
        'Callback URL': settings.MPESA_CALLBACK_URL,
        'Environment': settings.MPESA_ENVIRONMENT,
    }
    
    for key, value in config.items():
        status = "✓" if value and value != '...' else "✗"
        print(f"{status} {key}: {value if value else 'NOT SET'}")
    
    if not all([settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET, 
                settings.MPESA_PASSKEY]):
        print("\n⚠️  WARNING: Some credentials are missing!")
        print("Please update your .env file with Daraja credentials.")
        return False
    
    print("\n✓ All credentials configured!")
    return True


def test_access_token():
    """Test getting OAuth access token"""
    print("\n" + "=" * 60)
    print("TESTING ACCESS TOKEN")
    print("=" * 60)
    
    try:
        mpesa = MpesaAPI()
        token = mpesa.get_access_token()
        print(f"✓ Access token received: {token[:20]}...")
        return True
    except Exception as e:
        print(f"✗ Failed to get access token: {str(e)}")
        return False


def test_stk_push(phone_number="254710500108", amount=10):
    """Test STK Push"""
    print("\n" + "=" * 60)
    print("TESTING STK PUSH")
    print("=" * 60)
    print(f"Phone: {phone_number}")
    print(f"Amount: KES {amount}")
    print("\nInitiating STK Push...")
    
    try:
        mpesa = MpesaAPI()
        result = mpesa.stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference="TEST001",
            transaction_desc="Test Payment"
        )
        
        print("\nResponse:")
        print(json.dumps(result, indent=2))
        
        if result.get('ResponseCode') == '0':
            print("\n✓ STK Push sent successfully!")
            print(f"Checkout Request ID: {result.get('CheckoutRequestID')}")
            print("\nCheck your phone for the M-Pesa prompt!")
            return result.get('CheckoutRequestID')
        else:
            print(f"\n✗ STK Push failed: {result.get('ResponseDescription')}")
            return None
            
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return None


def test_query_status(checkout_request_id):
    """Test querying transaction status"""
    if not checkout_request_id:
        print("\nSkipping status query - no checkout request ID")
        return
    
    print("\n" + "=" * 60)
    print("TESTING TRANSACTION QUERY")
    print("=" * 60)
    print(f"Checkout Request ID: {checkout_request_id}")
    
    import time
    print("\nWaiting 10 seconds before querying...")
    time.sleep(10)
    
    try:
        mpesa = MpesaAPI()
        result = mpesa.query_transaction(checkout_request_id)
        
        print("\nQuery Response:")
        print(json.dumps(result, indent=2))
        
        if result.get('ResponseCode') == '0':
            print("\n✓ Transaction query successful!")
            print(f"Result: {result.get('ResultDesc')}")
        else:
            print(f"\n⚠️  Query returned: {result.get('ResponseDescription')}")
            
    except Exception as e:
        print(f"\n✗ Query error: {str(e)}")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "M-PESA INTEGRATION TEST" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Test 1: Check credentials
    if not test_credentials():
        print("\n❌ Please configure credentials first!")
        return
    
    # Test 2: Get access token
    if not test_access_token():
        print("\n❌ Cannot proceed without valid access token!")
        return
    
    # Test 3: STK Push
    print("\n\nReady to test STK Push!")
    print("=" * 60)
    
    # Ask for phone number
    use_default = input("\nUse default number (254710500108)? [Y/n]: ").strip().lower()
    
    if use_default in ['', 'y', 'yes']:
        phone_number = "254710500108"
    else:
        phone_number = input("Enter phone number (format: 254XXXXXXXXX): ").strip()
    
    # Ask for amount
    amount_input = input("Enter amount in KES [default: 10]: ").strip()
    amount = int(amount_input) if amount_input else 10
    
    checkout_request_id = test_stk_push(phone_number, amount)
    
    # Test 4: Query status (optional)
    if checkout_request_id:
        query = input("\nQuery transaction status? [Y/n]: ").strip().lower()
        if query in ['', 'y', 'yes']:
            test_query_status(checkout_request_id)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check your phone for STK push prompt (if sent)")
    print("2. Monitor ngrok dashboard: http://localhost:4040")
    print("3. Check backend logs for callback processing")
    print("4. Test through frontend: cd frontend && npm run dev")
    print("\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
