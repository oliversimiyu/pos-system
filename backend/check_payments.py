#!/usr/bin/env python
"""
Check recent payment callbacks
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_backend.settings')
django.setup()

from apps.payments.models import Payment, PaymentCallback
from django.utils import timezone
from datetime import timedelta

# Get recent payments (last 30 minutes)
recent_time = timezone.now() - timedelta(minutes=30)
recent_payments = Payment.objects.filter(
    initiated_at__gte=recent_time
).order_by('-initiated_at')

print("=" * 60)
print("RECENT PAYMENTS (Last 30 minutes)")
print("=" * 60)

for payment in recent_payments:
    print(f"\nPayment ID: {payment.id}")
    print(f"Transaction Ref: {payment.transaction_reference}")
    print(f"Method: {payment.method}")
    print(f"Amount: {payment.amount}")
    print(f"Status: {payment.status}")
    print(f"Initiated: {payment.initiated_at}")
    print(f"Phone: {payment.phone_number}")
    
    # Check for callbacks
    callbacks = payment.callbacks.all()
    if callbacks.exists():
        print(f"\nCallbacks ({callbacks.count()}):")
        for cb in callbacks:
            print(f"  - Type: {cb.callback_type}")
            print(f"    Success: {cb.success}")
            print(f"    Processed: {cb.processed}")
            print(f"    Received: {cb.received_at}")
            if cb.error_message:
                print(f"    Error: {cb.error_message}")
    else:
        print("\n⚠️  No callbacks received yet")
    
    print("-" * 60)

if not recent_payments.exists():
    print("\nNo recent payments found.")
