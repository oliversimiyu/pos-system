import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { salesAPI } from '../services/api/endpoints'
import { ArrowLeft, Calendar, User, CreditCard, Package, Receipt } from 'lucide-react'
import toast from 'react-hot-toast'
import { format } from 'date-fns'

export default function SaleDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [sale, setSale] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSale()
  }, [id])

  const fetchSale = async () => {
    setLoading(true)
    try {
      const response = await salesAPI.getById(id)
      setSale(response.data)
    } catch (error) {
      toast.error('Failed to load sale details')
      navigate('/sales')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      completed: 'badge-success',
      cancelled: 'badge-error',
    }
    return `badge ${badges[status] || 'badge-secondary'}`
  }

  const getPaymentStatusBadge = (status) => {
    const badges = {
      unpaid: 'badge-error',
      partial: 'badge-warning',
      paid: 'badge-success',
      refunded: 'badge-secondary',
    }
    return `badge ${badges[status] || 'badge-secondary'}`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!sale) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Sale not found</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/sales')}
            className="text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Sale Details</h1>
            <p className="text-gray-500">Receipt #{sale.sale_number}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <span className={getStatusBadge(sale.status)}>{sale.status}</span>
          <span className={getPaymentStatusBadge(sale.payment_status)}>
            {sale.payment_status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sale Information */}
        <div className="lg:col-span-2 space-y-6">
          {/* Items */}
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <Package className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold">Items</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>SKU</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Tax</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {sale.items?.map((item) => (
                    <tr key={item.id}>
                      <td>{item.product_name}</td>
                      <td className="font-mono text-sm">{item.product_sku}</td>
                      <td>{item.quantity}</td>
                      <td>Ksh {parseFloat(item.unit_price).toFixed(2)}</td>
                      <td>Ksh {parseFloat(item.tax_amount || 0).toFixed(2)}</td>
                      <td className="font-semibold">
                        Ksh {parseFloat(item.total).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Payments */}
          {sale.payments && sale.payments.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-4">
                <CreditCard className="w-5 h-5 text-primary-600" />
                <h2 className="text-lg font-semibold">Payment History</h2>
              </div>
              <div className="space-y-3">
                {sale.payments.map((payment) => (
                  <div
                    key={payment.id}
                    className="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
                  >
                    <div>
                      <p className="font-medium">
                        {payment.method === 'mpesa' ? 'M-Pesa' : 
                         payment.method === 'airtel' ? 'Airtel Money' :
                         payment.method === 'card' ? 'Card' :
                         payment.method === 'cash' ? 'Cash' :
                         payment.method}
                      </p>
                      <p className="text-sm text-gray-500">
                        {payment.transaction_reference}
                      </p>
                      {payment.phone_number && (
                        <p className="text-sm text-gray-500">{payment.phone_number}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">
                        Ksh {parseFloat(payment.amount).toFixed(2)}
                      </p>
                      <span className={`badge ${
                        payment.status === 'success' ? 'badge-success' :
                        payment.status === 'failed' ? 'badge-error' :
                        'badge-warning'
                      }`}>
                        {payment.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Summary Sidebar */}
        <div className="space-y-6">
          {/* Sale Summary */}
          <div className="card">
            <div className="flex items-center gap-2 mb-4">
              <Receipt className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold">Summary</h2>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium">
                  Ksh {parseFloat(sale.subtotal || 0).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tax</span>
                <span className="font-medium">
                  Ksh {parseFloat(sale.tax_amount || 0).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Discount</span>
                <span className="font-medium">
                  Ksh {parseFloat(sale.discount_amount || 0).toFixed(2)}
                </span>
              </div>
              <div className="border-t pt-3 flex justify-between text-lg">
                <span className="font-semibold">Total</span>
                <span className="font-bold text-primary-600">
                  Ksh {parseFloat(sale.total).toFixed(2)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Amount Paid</span>
                <span className="font-medium">
                  Ksh {parseFloat(sale.amount_paid || 0).toFixed(2)}
                </span>
              </div>
              {sale.amount_paid < sale.total && (
                <div className="flex justify-between text-red-600">
                  <span>Balance Due</span>
                  <span className="font-semibold">
                    Ksh {(parseFloat(sale.total) - parseFloat(sale.amount_paid || 0)).toFixed(2)}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Sale Info */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Information</h2>
            <div className="space-y-3">
              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Date</p>
                  <p className="font-medium">
                    {format(new Date(sale.created_at), 'MMM dd, yyyy HH:mm')}
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <User className="w-5 h-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-500">Cashier</p>
                  <p className="font-medium">{sale.cashier_name}</p>
                </div>
              </div>
              {sale.payment_method && (
                <div className="flex items-start gap-3">
                  <CreditCard className="w-5 h-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-sm text-gray-500">Payment Method</p>
                    <p className="font-medium">{sale.payment_method}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
