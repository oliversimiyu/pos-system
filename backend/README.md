# 🧾 Web-Based POS System - Backend API

A comprehensive Point of Sale (POS) system backend built with Django REST Framework, featuring integrated payment gateways (M-Pesa, Airtel Money, Card Payments), inventory management, sales tracking, and barcode scanner support.

## 🚀 Features

### Core Modules
- **👥 User Management**: Role-based access (Admin, Cashier)
- **📦 Products**: CRUD operations with categories, pricing, barcode support
- **💰 Sales**: Complete checkout flow with cart management
- **📊 Inventory**: Real-time stock tracking, low stock alerts, stock counts
- **💳 Payments**: Multi-payment method support (Cash, M-Pesa, Airtel Money, Cards)
- **📈 Reports**: Sales, inventory, and profit/loss reports

### Payment Integrations
- **M-Pesa Daraja API**: STK Push, callbacks, transaction verification
- **Airtel Money OpenAPI**: Payment initiation and webhooks
- **Card Payment Gateway**: Generic integration (Pesapal/Flutterwave compatible)
- **Split Payments**: Support for multiple payment methods per sale

### Special Features
- **Barcode Scanner Support**: Fast product lookup via barcode
- **Stock Movements**: Track all inventory changes
- **Payment Callbacks**: Automated webhook processing
- **Refund Management**: Process payment refunds
- **Dashboard Statistics**: Real-time business metrics

## 🛠️ Technology Stack

- **Framework**: Django 4.2 + Django REST Framework 3.16
- **Database**: PostgreSQL
- **Authentication**: Token-based (REST Framework)
- **API Documentation**: Swagger/OpenAPI (drf-yasg)
- **Image Processing**: Pillow
- **Date Utilities**: python-dateutil

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Virtual environment (recommended)

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pos-system/backend
```

### 2. Create Virtual Environment
```bash
python -m venv ../.venv
source ../.venv/bin/activate  # On Windows: ..\.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Copy the example environment file and configure:
```bash
cp env.example .env
```

Edit `.env` with your settings:
```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=pos_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# M-Pesa (Get from Safaricom Daraja)
MPESA_CONSUMER_KEY=your-key
MPESA_CONSUMER_SECRET=your-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/payments/webhooks/mpesa/callback/
MPESA_ENVIRONMENT=sandbox

# Airtel Money
AIRTEL_CLIENT_ID=your-client-id
AIRTEL_CLIENT_SECRET=your-client-secret
AIRTEL_CALLBACK_URL=https://yourdomain.com/api/payments/webhooks/airtel/callback/

# Card Gateway
PAYMENT_GATEWAY_API_KEY=your-api-key
PAYMENT_GATEWAY_SECRET=your-secret
```

### 5. Database Setup
```bash
# Create PostgreSQL database
createdb pos_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Server will start at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access:
- **Swagger UI**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/
- **Admin Panel**: http://localhost:8000/admin/

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/register/` - Register new user (admin only)

### Products
- `GET /api/products/` - List all products
- `POST /api/products/` - Create product
- `GET /api/products/{id}/` - Get product details
- `GET /api/products/barcode/{code}/` - **Get product by barcode** (for scanner)
- `GET /api/products/low_stock/` - Get low stock products
- `GET /api/products/categories/` - List categories

### Sales
- `GET /api/sales/sales/` - List all sales
- `POST /api/sales/sales/` - Create new sale/checkout
- `GET /api/sales/sales/{id}/` - Get sale details
- `POST /api/sales/sales/{id}/cancel/` - Cancel sale
- `GET /api/sales/sales/today/` - Today's sales

### Inventory
- `GET /api/inventory/movements/` - Stock movements history
- `POST /api/inventory/movements/` - Create stock movement
- `GET /api/inventory/alerts/` - Stock alerts
- `GET /api/inventory/alerts/active/` - Active alerts only
- `POST /api/inventory/counts/` - Create stock count
- `POST /api/inventory/counts/{id}/complete/` - Complete stock count

### Payments
- `POST /api/payments/payments/initiate/` - **Initiate payment** (M-Pesa/Airtel/Card)
- `GET /api/payments/payments/` - List payments
- `POST /api/payments/payments/{id}/verify/` - Verify payment status
- `POST /api/payments/refunds/` - Request refund
- `POST /api/payments/webhooks/mpesa/callback/` - M-Pesa webhook (public)
- `POST /api/payments/webhooks/airtel/callback/` - Airtel webhook (public)
- `POST /api/payments/webhooks/card/callback/` - Card gateway webhook (public)

### Reports
- `GET /api/reports/sales/?period=today` - Sales report (today/week/month/year/custom)
- `GET /api/reports/inventory/` - Inventory report
- `GET /api/reports/profit/?period=month` - Profit/loss report
- `GET /api/reports/dashboard/` - Dashboard statistics

## 💳 Payment Flow Examples

### M-Pesa STK Push
```json
POST /api/payments/payments/initiate/
{
  "sale": 1,
  "method": "mpesa",
  "amount": "1000.00",
  "phone_number": "254712345678"
}
```

### Airtel Money
```json
POST /api/payments/payments/initiate/
{
  "sale": 1,
  "method": "airtel",
  "amount": "1000.00",
  "phone_number": "254787654321"
}
```

### Cash Payment
```json
POST /api/payments/payments/initiate/
{
  "sale": 1,
  "method": "cash",
  "amount": "1000.00"
}
```

## 🔍 Barcode Scanner Integration

The system supports USB/Bluetooth HID barcode scanners:

```javascript
// Frontend example - auto-focus input for scanner
<input 
  ref={scannerInput}
  onKeyPress={(e) => {
    if (e.key === 'Enter') {
      // Barcode scanned
      fetch(`/api/products/barcode/${e.target.value}/`)
        .then(res => res.json())
        .then(product => addToCart(product))
    }
  }}
/>
```

## 📊 Database Schema

### Main Tables
- `users` - User accounts with roles
- `categories` - Product categories
- `products` - Products with barcode, pricing, stock
- `sales` - Sales/orders
- `sale_items` - Line items in sales
- `payments` - Payment transactions
- `payment_callbacks` - Webhook logs
- `stock_movements` - Inventory changes
- `stock_alerts` - Low stock notifications
- `stock_counts` - Physical inventory counts
- `refunds` - Payment refunds

## 🔒 Security Notes

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use HTTPS in production** for payment webhooks
3. **Validate webhook signatures** from payment gateways
4. **Implement rate limiting** for public endpoints
5. **Use strong SECRET_KEY** in production

## 🚀 Production Deployment

### Pre-deployment Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up SSL/TLS certificates
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up production database
- [ ] Configure static files (collectstatic)
- [ ] Set up Gunicorn/uWSGI
- [ ] Configure Nginx/Apache reverse proxy
- [ ] Set up payment gateway webhooks
- [ ] Enable database backups
- [ ] Configure logging and monitoring

### Example Gunicorn Command
```bash
gunicorn pos_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Check coverage
coverage run --source='.' manage.py test
coverage report
```

## 📝 Development Notes

### Adding New Payment Gateway
1. Create service file in `payments/{gateway}/services.py`
2. Implement `initiate_payment()`, `verify_payment()`, `process_callback()`
3. Add URL route in `payments/{gateway}/urls.py`
4. Update `apps/payments/views.py` to route to new gateway

### Creating Custom Reports
Add new views in `apps/reports/views.py`:
```python
class CustomReportView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Your report logic
        return Response(data)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Support

For support and questions:
- Create an issue in the repository
- Email: support@possystem.local

## 🗺️ Roadmap

**Phase 1** ✅
- Core POS functionality
- User management
- Product catalog
- Sales processing

**Phase 2** ✅
- Inventory management
- Payment integrations
- Reports and analytics

**Phase 3** (Planned)
- PWA offline support
- Multi-store management
- Loyalty program
- Receipt printing (ESC/POS)
- Mobile app

**Phase 4** (Future)
- AI-powered sales forecasting
- Advanced analytics
- Integration with accounting software
- Customer relationship management

---

**Built with ❤️ for modern retail businesses**
