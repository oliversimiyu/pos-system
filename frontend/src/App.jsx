import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import Layout from './components/Layout'

// Pages
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import POSCheckout from './pages/POSCheckout'
import Products from './pages/Products'
import ProductForm from './pages/ProductForm'
import Sales from './pages/Sales'
import SaleDetail from './pages/SaleDetail'
import Inventory from './pages/Inventory'
import Payments from './pages/Payments'
import Reports from './pages/Reports'
import Users from './pages/Users'
import UserForm from './pages/UserForm'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="pos" element={<POSCheckout />} />
          
          <Route path="products">
            <Route index element={<Products />} />
            <Route path="new" element={<ProductForm />} />
            <Route path=":id/edit" element={<ProductForm />} />
          </Route>
          
          <Route path="sales">
            <Route index element={<Sales />} />
            <Route path=":id" element={<SaleDetail />} />
          </Route>
          
          <Route path="inventory" element={<Inventory />} />
          <Route path="payments" element={<Payments />} />
          <Route path="reports" element={<Reports />} />
          
          <Route path="users">
            <Route index element={<Users />} />
            <Route path="new" element={<UserForm />} />
            <Route path=":id/edit" element={<UserForm />} />
          </Route>
        </Route>
        
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
