# Frontend README

## POS System - React Frontend

Modern, responsive React frontend for the POS System with barcode scanner support, multi-payment integration, and real-time inventory management.

## Tech Stack

- **React 18.2** - UI framework
- **Vite 5.0** - Build tool and dev server
- **React Router 6** - Client-side routing
- **Axios** - HTTP client
- **Zustand** - State management
- **Tailwind CSS** - Styling
- **Recharts** - Data visualization
- **React Hot Toast** - Notifications
- **Lucide React** - Icons

## Features

### 1. Authentication
- Token-based authentication with Django backend
- Protected routes
- Auto-redirect on session expiry

### 2. POS Checkout
- **Barcode Scanner Integration**
  - Auto-focus input field
  - Quick product lookup by barcode
  - Manual product search fallback
- Shopping cart with real-time updates
- Multi-payment method support:
  - Cash (with change calculation)
  - M-Pesa (STK Push integration)
  - Airtel Money
  - Card payments
- Stock validation before checkout

### 3. Product Management
- CRUD operations for products
- Category management
- Barcode assignment
- Stock tracking
- Low stock alerts
- Reorder level configuration

### 4. Sales Tracking
- Complete sales history
- Receipt generation
- Transaction details
- Date range filtering
- Status tracking (Pending, Completed, Cancelled)

### 5. Inventory Management
- Real-time stock movements (IN/OUT)
- Stock alerts and notifications
- Stock count management
- Movement history with audit trail

### 6. Payment Processing
- Multi-gateway support
- Payment status tracking
- Transaction history
- Refund management
- Real-time payment verification

### 7. Reports & Analytics
- **Sales Reports**
  - Total sales, transactions, average sale
  - Sales trends (daily, weekly, monthly)
  - Top-selling products
- **Inventory Reports**
  - Stock levels by category
  - Low stock analysis
  - Stock valuation
- **Profit Analysis**
  - Revenue vs cost comparison
  - Profit margins
  - Trend analysis

### 8. Dashboard
- Quick stats overview
- Today's sales summary
- Low stock alerts
- Recent transactions
- Sales trends visualization

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env to set VITE_API_URL if backend is not on localhost:8000
```

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── Layout.jsx     # Main layout with sidebar
│   │   ├── Header.jsx     # Top navigation bar
│   │   ├── Sidebar.jsx    # Side navigation menu
│   │   ├── ProtectedRoute.jsx  # Auth guard
│   │   └── PaymentModal.jsx    # Payment processing UI
│   ├── pages/             # Page components
│   │   ├── Login.jsx      # Authentication page
│   │   ├── Dashboard.jsx  # Main dashboard
│   │   ├── POSCheckout.jsx     # POS checkout with barcode
│   │   ├── Products.jsx   # Product listing
│   │   ├── ProductForm.jsx     # Product create/edit
│   │   ├── Sales.jsx      # Sales history
│   │   ├── Inventory.jsx  # Inventory management
│   │   ├── Payments.jsx   # Payment transactions
│   │   └── Reports.jsx    # Analytics & reports
│   ├── services/          # API integration
│   │   └── api/
│   │       ├── client.js  # Axios instance with interceptors
│   │       └── endpoints.js    # API endpoint functions
│   ├── context/           # React context providers
│   │   └── AuthContext.jsx     # Authentication state
│   ├── App.jsx            # Root component with routing
│   ├── main.jsx           # React entry point
│   └── index.css          # Global styles + Tailwind
├── index.html             # HTML template
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS config
├── postcss.config.js      # PostCSS config
└── package.json           # Dependencies
```

## Key Components

### Barcode Scanner (POSCheckout.jsx)
- Auto-focus input for quick scanning
- Enter key submits barcode
- Automatic product lookup
- Visual feedback for successful/failed scans

### Payment Modal (PaymentModal.jsx)
- Multi-payment method UI
- Real-time M-Pesa/Airtel payment status polling
- Change calculation for cash payments
- Payment confirmation handling

### API Client (services/api/client.js)
- Token authentication interceptor
- Error handling with toast notifications
- Auto-redirect on 401 errors
- Base URL configuration

## API Integration

All API calls use the centralized client with endpoints organized by resource:

```javascript
import { productsAPI, salesAPI, paymentsAPI } from '@/services/api/endpoints'

// Example: Barcode lookup
const product = await productsAPI.getByBarcode('123456789')

// Example: Create sale with payment
const sale = await salesAPI.create({
  items: [...],
  payment_method: 'MPESA',
  amount_paid: 1000
})
```

## Barcode Scanner Hardware

The POS checkout page is designed to work with USB barcode scanners that emulate keyboard input. The scanner should:

1. Send barcode digits as keyboard input
2. Automatically press Enter after scanning
3. Be configured to send raw barcode data (no prefix/suffix unless needed)

**Configuration:**
- Input field is auto-focused after each scan
- Enter key triggers product lookup
- Failed scans show error toast with audio/visual feedback

## Payment Gateway Integration

### M-Pesa
- STK Push initiated from frontend
- Real-time status polling
- 2-minute timeout for user confirmation
- Automatic payment verification

### Airtel Money
- Similar flow to M-Pesa
- Phone number validation
- Payment status tracking

### Card Payments
- Generic card gateway integration
- Card number validation
- Mock processing (implement real gateway as needed)

### Cash
- Manual amount entry
- Automatic change calculation
- Instant transaction completion

## Customization

### Branding
Edit Tailwind config to change primary colors:
```javascript
// tailwind.config.js
theme: {
  extend: {
    colors: {
      primary: { /* your brand colors */ }
    }
  }
}
```

### API Configuration
Update base URL in `.env`:
```
VITE_API_URL=https://your-backend-domain.com/api
```

## Development Tips

1. **Hot Module Replacement**: Vite provides instant HMR - changes reflect immediately
2. **API Proxy**: Vite dev server proxies `/api` requests to Django backend
3. **State Management**: Use Zustand for global state (auth is in Context for simplicity)
4. **Form Validation**: Basic HTML5 validation used - enhance with libraries as needed
5. **Error Handling**: All errors show toast notifications automatically

## Testing

Currently manual testing is recommended. Test checklist:

- [ ] Login/logout flow
- [ ] Barcode scanning and product lookup
- [ ] Cart operations (add, remove, update quantity)
- [ ] All payment methods
- [ ] Product CRUD operations
- [ ] Sales history and filtering
- [ ] Inventory movements
- [ ] Report generation
- [ ] Dashboard stats

## Deployment

### Option 1: Static Hosting (Netlify, Vercel, etc.)
```bash
npm run build
# Deploy dist/ folder
```

Configure redirects for React Router:
```
/* /index.html 200
```

### Option 2: Serve with Django
Build the frontend and copy `dist/` contents to Django's `static/` directory. Configure Django to serve the React app.

### Option 3: Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

## Troubleshooting

### CORS Errors
- Ensure Django `CORS_ALLOWED_ORIGINS` includes frontend URL
- Check `CORS_ALLOW_CREDENTIALS = True` in Django settings

### Authentication Issues
- Clear localStorage and try again
- Check token format in network tab
- Verify backend authentication endpoint

### Barcode Scanner Not Working
- Test scanner in text editor to verify it's working
- Ensure input field is focused
- Check scanner configuration (no extra characters)

### Payment Polling Timeout
- M-Pesa/Airtel polling stops after 2 minutes
- User must complete payment within timeout window
- Check backend webhook configuration

## Future Enhancements

- [ ] PWA support with offline capabilities
- [ ] Websocket for real-time updates
- [ ] Advanced reporting with PDF export
- [ ] Multi-store support
- [ ] Employee shift management
- [ ] Customer loyalty program
- [ ] Receipt printer integration
- [ ] Advanced inventory forecasting

## Support

For issues or questions:
1. Check backend logs for API errors
2. Check browser console for frontend errors
3. Verify network requests in DevTools
4. Review authentication token in localStorage

## License

Part of the POS System project. See main README for licensing details.
