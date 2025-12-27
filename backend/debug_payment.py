#!/usr/bin/env python
"""Debug payment initiation errors"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_backend.settings')
django.setup()

from apps.payments.serializers import PaymentInitiateSerializer
from apps.sales.models import Sale
from django.contrib.auth import get_user_model

User = get_user_model()

# Get a user for testing
try:
    user = User.objects.first()
    if not user:
        print("❌ No users found. Create a user first.")
        sys.exit(1)
        
    # Get or create a test sale
    sale = Sale.objects.filter(payment_status__in=['unpaid', 'partial']).first()
    
    if not sale:
        print("❌ No unpaid sales found. Create a sale first.")
        sys.exit(1)
    
    print(f"✓ Testing with Sale: {sale.sale_number}")
    print(f"  Total: {sale.total}")
    print(f"  Paid: {sale.amount_paid}")
    print(f"  Remaining: {sale.total - sale.amount_paid}")
    print(f"  Status: {sale.payment_status}")
    
    # Test payment data
    test_data = {
        'sale': sale.id,
        'method': 'mpesa',
        'amount': 10.00,
        'phone_number': '254710500108'
    }
    
    print(f"\n✓ Test payment data:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    
    # Validate
    serializer = PaymentInitiateSerializer(data=test_data, context={'request': type('obj', (object,), {'user': user})()})
    
    if serializer.is_valid():
        print("\n✅ Validation passed!")
        payment = serializer.save()
        print(f"✓ Payment created: {payment.transaction_reference}")
    else:
        print("\n❌ Validation failed:")
        for field, errors in serializer.errors.items():
            print(f"  {field}: {', '.join(errors)}")
            
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
