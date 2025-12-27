# Setup ngrok for M-Pesa Callbacks

## Install ngrok

```bash
# Option 1: Download from ngrok.com
https://ngrok.com/download

# Option 2: Using snap (Ubuntu/Linux)
sudo snap install ngrok

# Option 3: Using brew (Mac)
brew install ngrok
```

## Run ngrok

Open a NEW terminal and run:

```bash
ngrok http 8000
```

You'll see output like:
```
Forwarding   https://abc123def456.ngrok.io -> http://localhost:8000
```

## Update .env

Copy the `https://` URL (e.g., `https://abc123def456.ngrok.io`) and update your `.env`:

```env
MPESA_CALLBACK_URL=https://abc123def456.ngrok.io/api/payments/webhooks/mpesa/callback/
```

## Restart Backend

After updating `.env`, restart your Django server:
```bash
# Stop the current server (Ctrl+C)
# Then restart:
python manage.py runserver
```

## Test from Frontend

1. Start frontend: `npm run dev`
2. Create a sale
3. Try M-Pesa payment with your phone number: 254710500108
4. Enter PIN 1234 when prompted

## Monitor

- **ngrok dashboard**: http://localhost:4040
- View incoming M-Pesa callbacks in real-time
