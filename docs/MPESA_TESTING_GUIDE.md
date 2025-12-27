# M-Pesa Daraja API Integration Guide

## Prerequisites Completed ✓
- [x] Created sandbox app on Daraja Portal
- [x] Integration code is ready

## Next Steps for Testing

### 1. Configure Daraja Sandbox Credentials

1. **Login to Daraja Portal**: https://developer.safaricom.co.ke/
2. **Navigate to your sandbox app** and collect:
   - Consumer Key
   - Consumer Secret
   - Test Credentials (Passkey)

3. **Update `/backend/.env` file**:
   ```env
   MPESA_CONSUMER_KEY=your_consumer_key_here
   MPESA_CONSUMER_SECRET=your_consumer_secret_here
   MPESA_SHORTCODE=174379
   MPESA_PASSKEY=your_passkey_here
   MPESA_CALLBACK_URL=https://your-ngrok-url.ngrok.io/api/payments/webhooks/mpesa/callback/
   MPESA_ENVIRONMENT=sandbox
   ```

### 2. Setup ngrok for Callback URL

M-Pesa needs a public URL to send callbacks. Install and run ngrok:

```bash
# Install ngrok (if not installed)
# Download from https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000
```

This will give you a URL like: `https://abc123.ngrok.io`

Update your `.env`:
```env
MPESA_CALLBACK_URL=https://abc123.ngrok.io/api/payments/webhooks/mpesa/callback/
```

**Important**: Update the callback URL in your Daraja app settings too!

### 3. Start Your Backend Server

```bash
cd backend
source ../.venv/bin/activate  # if not already activated
python manage.py runserver
```

### 4. Test M-Pesa Integration

#### Option A: Using the POS Frontend
1. Start frontend: `cd frontend && npm run dev`
2. Create a sale and select M-Pesa payment
3. Enter test phone number: `254708374149` (Safaricom sandbox test number)
4. You'll receive an STK push prompt on the test app

#### Option B: Using cURL/Postman

**Step 1: Create a Sale**
```bash
curl -X POST http://localhost:8000/api/sales/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "items": [{"product": 1, "quantity": 1, "price": 100}],
    "total_amount": 100
  }'
```

**Step 2: Initiate M-Pesa Payment**
```bash
curl -X POST http://localhost:8000/api/payments/initiate/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "sale": 1,
    "method": "mpesa",
    "amount": 100,
    "phone_number": "254708374149"
  }'
```

### 5. Safaricom Sandbox Test Credentials

**Test Phone Numbers:**
- `254708374149` - Returns success
- `254708374150` - Returns insufficient balance
- `254708374151` - Returns wrong PIN

**Test STK Push:**
- When prompted, enter PIN: `1234`

### 6. Monitor & Debug

**Check Payment Status:**
```bash
curl http://localhost:8000/api/payments/{payment_id}/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Check ngrok dashboard:**
Visit: `http://localhost:4040` to see incoming callbacks

**Check Django logs:**
The terminal running `manage.py runserver` will show request logs

### 7. Verify Callback Processing

After STK push completes:
1. Check ngrok dashboard for incoming POST to `/api/payments/webhooks/mpesa/callback/`
2. Check payment status - should change from `processing` to `success` or `failed`
3. Verify sale `payment_status` is updated

### 8. Common Issues & Solutions

**Issue: "Failed to get access token"**
- Verify Consumer Key & Secret are correct
- Check internet connection
- Ensure MPESA_ENVIRONMENT=sandbox

**Issue: "Callback not received"**
- Verify ngrok is running
- Check callback URL matches ngrok URL
- Update callback URL in Daraja portal settings
- Check ngrok dashboard for incoming requests

**Issue: "Invalid Access Token"**
- Access tokens expire after ~1 hour
- The system automatically generates new ones

**Issue: STK Push not showing on phone**
- Use correct test phone format: `254708374149`
- Ensure you're using Safaricom sandbox test numbers
- Check Daraja portal for API call logs

### 9. Moving to Production

When ready for production:
1. Create production app on Daraja Portal
2. Get production credentials & shortcode
3. Go Live approval from Safaricom (requires documentation)
4. Update `.env`:
   ```env
   MPESA_ENVIRONMENT=production
   MPESA_CONSUMER_KEY=prod_key
   MPESA_CONSUMER_SECRET=prod_secret
   MPESA_SHORTCODE=your_actual_shortcode
   MPESA_PASSKEY=prod_passkey
   MPESA_CALLBACK_URL=https://your-domain.com/api/payments/webhooks/mpesa/callback/
   ```

## Testing Checklist

- [ ] Credentials configured in `.env`
- [ ] ngrok running and URL updated
- [ ] Backend server running
- [ ] Test STK push with sandbox number
- [ ] Callback received and processed
- [ ] Payment status updated correctly
- [ ] Sale payment status updated
- [ ] Test failed payment scenario
- [ ] Test timeout scenario

## Useful Links

- Daraja Portal: https://developer.safaricom.co.ke/
- Daraja Documentation: https://developer.safaricom.co.ke/docs
- Test credentials: https://developer.safaricom.co.ke/test_credentials
- API Logs: Check your Daraja app dashboard
