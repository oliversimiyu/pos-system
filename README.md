# POS System

A modern, full-stack Point of Sale (POS) system built with React and Django, featuring barcode scanner support, multi-payment gateway integration (M-Pesa, Airtel Money, Card payments), and comprehensive inventory management.

## Features

### Core Functionality
- **POS Checkout** - Fast checkout with barcode scanner integration and manual product search
- **Multi-Payment Support** - Cash, M-Pesa STK Push, Airtel Money, and Card payments
- **Inventory Management** - Real-time stock tracking, alerts, and stock count management
- **Product Management** - Complete CRUD operations with barcode assignment and categories
- **Sales Tracking** - Comprehensive sales history with receipt generation
- **Reports & Analytics** - Sales reports, inventory reports, and profit analysis with charts
- **User Authentication** - Secure token-based authentication with role-based access

### Payment Integrations
- **M-Pesa Daraja API** - STK Push with real-time callback handling
- **Airtel Money OpenAPI** - Payment initiation and webhook verification
- **Card Gateway** - Generic card payment integration (customizable)
- **Cash Payments** - With automatic change calculation

### Additional Features
- Barcode scanner support for quick product lookup
- Low stock alerts and notifications
- Stock movement tracking with audit trail
- Dashboard with real-time statistics
- Responsive design for desktop and tablet use

## Tech Stack

### Backend
- Django 4.2.27
- Django REST Framework 3.16.1
- PostgreSQL (recommended) / SQLite (development)
- Token-based authentication
- Swagger/OpenAPI documentation

### Frontend
- React 18.2
- Vite 5.0
- Tailwind CSS 3.3
- Axios for API calls
- Recharts for data visualization
- React Router for navigation

## Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 12+ (recommended for production)
- Git

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/oliversimiyu/pos-system.git
cd pos-system
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/Mac:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and configure your settings:
# - SECRET_KEY (generate a secure key)
# - DATABASE_URL (PostgreSQL connection string)
# - MPESA_* (M-Pesa API credentials)
# - AIRTEL_* (Airtel Money API credentials)
# - ALLOWED_HOSTS
# - CORS_ALLOWED_ORIGINS

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env if backend is not on localhost:8000
# VITE_API_URL=http://localhost:8000/api

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Running the Application

### Development Mode

1. **Start Backend** (Terminal 1):
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python manage.py runserver
```

2. **Start Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```

3. **Access the Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - Django Admin: http://localhost:8000/admin
   - API Documentation: http://localhost:8000/swagger

### Production Build

#### Backend
```bash
cd backend
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn pos_backend.wsgi:application --bind 0.0.0.0:8000
```

#### Frontend
```bash
cd frontend
npm run build
# Serve the dist/ folder with nginx or another static server
```

## Environment Configuration

### Backend (.env)
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/pos_db
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# M-Pesa Configuration
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/payments/webhooks/mpesa/callback/

# Airtel Money Configuration
AIRTEL_CLIENT_ID=your-client-id
AIRTEL_CLIENT_SECRET=your-client-secret
AIRTEL_CALLBACK_URL=https://yourdomain.com/api/payments/webhooks/airtel/callback/

# Card Gateway Configuration
CARD_GATEWAY_API_KEY=your-api-key
CARD_GATEWAY_MERCHANT_ID=your-merchant-id
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000/api
```

## Database Setup

### PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL
# Create database
createdb pos_db

# Create user
createuser pos_user -P

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE pos_db TO pos_user;"

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://pos_user:password@localhost:5432/pos_db
```

### SQLite (Development Only)

SQLite is configured by default for development. No additional setup required.

## Barcode Scanner Setup

The POS checkout page supports USB barcode scanners that emulate keyboard input:

1. Connect your USB barcode scanner
2. Configure the scanner to:
   - Send raw barcode data
   - Automatically press Enter after scanning
   - No prefix/suffix (or configure in settings if needed)
3. The POS checkout input field will auto-focus and accept scans

## Payment Gateway Setup

### M-Pesa Daraja API

1. Register at [Daraja Portal](https://developer.safaricom.co.ke/)
2. Create an app to get Consumer Key and Consumer Secret
3. Get your STK Push credentials (Shortcode and Passkey)
4. Configure callback URL to receive payment confirmations
5. Update backend `.env` with your credentials

### Airtel Money

1. Contact Airtel Business to get API access
2. Obtain Client ID and Client Secret
3. Configure callback URL
4. Update backend `.env` with your credentials

### Card Payments

Integrate with your preferred payment gateway (Stripe, Flutterwave, etc.) by updating the `payments/cards/services.py` implementation.

## API Documentation

Once the backend is running, access interactive API documentation:

- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

## Default Login

After creating a superuser, you can log in to both the Django admin and the frontend application with those credentials.

## Common Tasks

### Create Sample Data
```bash
cd backend
python manage.py shell
# Use Django shell to create sample categories, products, etc.
```

### Run Tests
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests (if configured)
cd frontend
npm test
```

### View Logs
```bash
# Backend logs
cd backend
tail -f logs/debug.log  # if logging to file

# Frontend dev server shows logs in terminal
```

## Troubleshooting

### Backend Issues

**Database connection errors:**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database and user exist

**CORS errors:**
- Add frontend URL to CORS_ALLOWED_ORIGINS in settings.py
- Ensure CORS_ALLOW_CREDENTIALS = True

**Migration errors:**
- Delete migration files (except __init__.py) and recreate
- Drop database and start fresh if needed

### Frontend Issues

**API connection errors:**
- Verify backend is running on port 8000
- Check VITE_API_URL in frontend/.env
- Check browser console for CORS errors

**Build errors:**
- Delete node_modules and package-lock.json
- Run `npm install` again
- Clear npm cache: `npm cache clean --force`

**Authentication not working:**
- Clear browser localStorage
- Check token in Network tab
- Verify backend authentication endpoint

## Deployment

### Backend Deployment Options
- **Heroku**: Use Heroku Postgres and configure environment variables
- **DigitalOcean**: Deploy with App Platform or Droplet with Nginx + Gunicorn
- **AWS**: Use EC2 with RDS for database
- **Docker**: Use provided Dockerfile (create one for containerization)

### Frontend Deployment Options
- **Vercel**: Connect GitHub repo and deploy automatically
- **Netlify**: Build command: `npm run build`, Publish directory: `dist`
- **Nginx**: Serve the `dist` folder as static files
- **With Backend**: Configure Django to serve React build files

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues, questions, or contributions:
- Open an issue on [GitHub](https://github.com/oliversimiyu/pos-system/issues)
- Check existing documentation in `backend/` and `frontend/` folders

## Acknowledgments

- M-Pesa Daraja API for payment integration
- Airtel Money API for mobile money support
- React and Django communities for excellent frameworks
