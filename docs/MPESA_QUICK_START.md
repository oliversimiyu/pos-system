# M-Pesa Testing Quick Start

## 1. Get Credentials from Daraja Portal
```
https://developer.safaricom.co.ke/
→ My Apps → Your Sandbox App → Keys
```

## 2. Update `.env` File
```bash
cd /home/codename/pos-system/backend
nano .env  # or use VS Code

# Update these lines:
MPESA_CONSUMER_KEY=your_key_here
MPESA_CONSUMER_SECRET=your_secret_here
MPESA_PASSKEY=your_passkey_here
```

## 3. Setup ngrok (for callbacks)
```bash
# Terminal 1: Start ngrok
ngrok http 8000

# Copy the https URL (e.g., https://abc123.ngrok.io)
# Update .env:
MPESA_CALLBACK_URL=https://abc123.ngrok.io/api/payments/webhooks/mpesa/callback/
```

## 4. Start Backend
```bash
# Terminal 2: Start Django
cd /home/codename/pos-system/backend
source ../.venv/bin/activate
python manage.py runserver
```

## 5. Run Test Script
```bash
# Terminal 3: Test M-Pesa
cd /home/codename/pos-system/backend
python test_mpesa.py
```

Follow the prompts:
- Phone: 254708374149 (test number)
- Amount: 10
- PIN when prompted: 1234

## 6. Monitor
- **ngrok dashboard**: http://localhost:4040
- **Backend logs**: Terminal 2
- **Callback**: Watch ngrok for POST request

## Test Numbers (Safaricom Sandbox)
- `254708374149` - Success
- `254708374150` - Insufficient balance  
- `254708374151` - Wrong PIN

## Check Payment Status
```bash
# In Python shell
python manage.py shell

from apps.payments.models import Payment
Payment.objects.latest('id')  # Check latest payment
```

## Troubleshooting
- **No access token**: Check credentials in .env
- **No callback**: Ensure ngrok is running and URL is correct
- **No STK push**: Use correct test number format (254...)

---
📚 Full guide: `/docs/MPESA_TESTING_GUIDE.md`
