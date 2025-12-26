# 🧪 API Testing Guide

Quick reference for testing the POS System API endpoints.

## Setup for Testing

### 1. Start the Server
```bash
source ../.venv/bin/activate
python manage.py runserver
```

### 2. Create Test User (Admin)
```bash
python manage.py createsuperuser
# Username: admin
# Password: admin123
```

### 3. Get Authentication Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Save the token for authenticated requests.

## Common Test Workflows

### Workflow 1: Complete Sale with Barcode Scanner

#### Step 1: Create Category
```bash
curl -X POST http://localhost:8000/api/products/categories/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "description": "Electronic products"
  }'
```

#### Step 2: Create Product with Barcode
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Wireless Mouse",
    "category": 1,
    "barcode": "1234567890123",
    "sku": "WM-001",
    "price": "1500.00",
    "cost_price": "1000.00",
    "tax": "16.00",
    "stock": 50,
    "low_stock_threshold": 10,
    "is_active": true
  }'
```

#### Step 3: Lookup Product by Barcode
```bash
curl -X GET http://localhost:8000/api/products/barcode/1234567890123/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Step 4: Create Sale (Checkout)
```bash
curl -X POST http://localhost:8000/api/sales/sales/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "John Doe",
    "customer_phone": "254712345678",
    "discount": "0",
    "amount_paid": "1740",
    "items": [
      {
        "product": 1,
        "quantity": 1
      }
    ]
  }'
```

### Workflow 2: M-Pesa Payment

#### Step 1: Initiate M-Pesa STK Push
```bash
curl -X POST http://localhost:8000/api/payments/payments/initiate/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sale": 1,
    "method": "mpesa",
    "amount": "1740.00",
    "phone_number": "254712345678"
  }'
```

#### Step 2: Verify Payment Status
```bash
curl -X POST http://localhost:8000/api/payments/payments/1/verify/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Workflow 3: Inventory Management

#### Step 1: Add Stock (Purchase)
```bash
curl -X POST http://localhost:8000/api/inventory/movements/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "movement_type": "purchase",
    "quantity": 20,
    "unit_cost": "1000.00",
    "notes": "Restocking from supplier"
  }'
```

#### Step 2: Get Low Stock Alerts
```bash
curl -X GET http://localhost:8000/api/inventory/alerts/active/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Step 3: Create Stock Count
```bash
curl -X POST http://localhost:8000/api/inventory/counts/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Monthly stock count"
  }'
```

#### Step 4: Add Items to Stock Count
```bash
curl -X POST http://localhost:8000/api/inventory/counts/1/add_item/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "physical_quantity": 68,
    "notes": "Counted by John"
  }'
```

#### Step 5: Complete Stock Count
```bash
curl -X POST http://localhost:8000/api/inventory/counts/1/complete/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Workflow 4: Reports & Analytics

#### Today's Sales Report
```bash
curl -X GET "http://localhost:8000/api/reports/sales/?period=today" \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Monthly Profit Report
```bash
curl -X GET "http://localhost:8000/api/reports/profit/?period=month" \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Inventory Report
```bash
curl -X GET http://localhost:8000/api/reports/inventory/ \
  -H "Authorization: Token YOUR_TOKEN"
```

#### Dashboard Statistics
```bash
curl -X GET http://localhost:8000/api/reports/dashboard/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## Testing Payment Webhooks

### M-Pesa Callback Test
```bash
curl -X POST http://localhost:8000/api/payments/webhooks/mpesa/callback/ \
  -H "Content-Type: application/json" \
  -d '{
    "Body": {
      "stkCallback": {
        "MerchantRequestID": "29115-34620561-1",
        "CheckoutRequestID": "ws_CO_191220191020363925",
        "ResultCode": 0,
        "ResultDesc": "The service request is processed successfully.",
        "CallbackMetadata": {
          "Item": [
            {
              "Name": "Amount",
              "Value": 1.00
            },
            {
              "Name": "MpesaReceiptNumber",
              "Value": "NLJ7RT61SV"
            },
            {
              "Name": "PhoneNumber",
              "Value": 254712345678
            }
          ]
        }
      }
    }
  }'
```

## Postman Collection

Import this collection for easier testing:

```json
{
  "info": {
    "name": "POS System API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "token",
      "value": "YOUR_TOKEN_HERE"
    }
  ]
}
```

## Common Issues & Solutions

### Issue: "Authentication credentials were not provided"
**Solution**: Add Authorization header with your token
```bash
-H "Authorization: Token YOUR_TOKEN_HERE"
```

### Issue: "Product not found with this barcode"
**Solution**: Ensure barcode exists and product is active
```bash
# List all products to check
curl -X GET http://localhost:8000/api/products/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Issue: "Insufficient stock"
**Solution**: Check product stock and add inventory
```bash
# Add stock
curl -X POST http://localhost:8000/api/inventory/movements/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "movement_type": "purchase",
    "quantity": 50,
    "unit_cost": "1000.00"
  }'
```

### Issue: M-Pesa "Failed to get access token"
**Solution**: Check your M-Pesa credentials in `.env`:
- MPESA_CONSUMER_KEY
- MPESA_CONSUMER_SECRET
- MPESA_ENVIRONMENT (sandbox/production)

## Batch Testing Script

Create `test_api.sh`:
```bash
#!/bin/bash

# Set variables
BASE_URL="http://localhost:8000"
TOKEN="your-token-here"

echo "Testing POS API..."

# Test 1: Get all products
echo "1. Fetching products..."
curl -s -X GET "$BASE_URL/api/products/" \
  -H "Authorization: Token $TOKEN" | jq

# Test 2: Create sale
echo "2. Creating sale..."
curl -s -X POST "$BASE_URL/api/sales/sales/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Customer",
    "discount": "0",
    "amount_paid": "1740",
    "items": [{"product": 1, "quantity": 1}]
  }' | jq

# Test 3: Get today's sales
echo "3. Today's sales..."
curl -s -X GET "$BASE_URL/api/sales/sales/today/" \
  -H "Authorization: Token $TOKEN" | jq

echo "Tests complete!"
```

Run with:
```bash
chmod +x test_api.sh
./test_api.sh
```

## Python Testing Script

```python
import requests

BASE_URL = "http://localhost:8000"
TOKEN = "your-token-here"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Test product creation
def test_create_product():
    data = {
        "name": "Test Product",
        "category": 1,
        "barcode": "9876543210987",
        "sku": "TEST-001",
        "price": "500.00",
        "cost_price": "300.00",
        "tax": "16.00",
        "stock": 100
    }
    response = requests.post(
        f"{BASE_URL}/api/products/",
        json=data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

# Test sale creation
def test_create_sale():
    data = {
        "customer_name": "Jane Smith",
        "discount": "0",
        "amount_paid": "580",
        "items": [
            {"product": 1, "quantity": 1}
        ]
    }
    response = requests.post(
        f"{BASE_URL}/api/sales/sales/",
        json=data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_create_product()
    test_create_sale()
```

---

**Happy Testing! 🧪**
