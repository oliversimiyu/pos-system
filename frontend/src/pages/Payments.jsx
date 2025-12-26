import { useState, useEffect } from 'react'
import { paymentsAPI } from '../services/api/endpoints'
import { Search, CreditCard, CheckCircle, XCircle, Clock } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function Payments() {
  const [payments, setPayments] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [methodFilter, setMethodFilter] = useState('')

  useEffect(() => {
    fetchPayments()
  }, [])

  const fetchPayments = async (params = {}) => {
    setLoading(true)
    try {
      const response = await paymentsAPI.getAll(params)
      setPayments(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to load payments')
    } finally {
      setLoading(false)
    }
  }

  const handleFilter = () => {
    const params = {}
    if (statusFilter) params.status = statusFilter
    if (methodFilter) params.method = methodFilter
    fetchPayments(params)
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-600" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-600" />
      default:
        return null
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      completed: 'badge-success',
      failed: 'badge-error',
    }
    return `badge ${badges[status] || ''}`
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Payments</h1>
      </div>

      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Payment Method
            </label>
            <select
              value={methodFilter}
              onChange={(e) => setMethodFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Methods</option>
              <option value="CASH">Cash</option>
              <option value="MPESA">M-Pesa</option>
              <option value="AIRTEL">Airtel Money</option>
              <option value="CARD">Card</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div className="flex items-end">
            <button onClick={handleFilter} className="btn btn-secondary w-full">
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Transaction ID</th>
                  <th>Method</th>
                  <th>Amount</th>
                  <th>Phone/Card</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th>Sale</th>
                </tr>
              </thead>
              <tbody>
                {payments.map((payment) => (
                  <tr key={payment.id}>
                    <td className="font-mono text-sm">{payment.transaction_id}</td>
                    <td>
                      <span className="badge badge-secondary">{payment.method}</span>
                    </td>
                    <td className="font-semibold">Ksh {payment.amount}</td>
                    <td>{payment.phone_number || payment.card_number || '-'}</td>
                    <td>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(payment.status)}
                        <span className={getStatusBadge(payment.status)}>
                          {payment.status}
                        </span>
                      </div>
                    </td>
                    <td>{format(new Date(payment.created_at), 'MMM dd, yyyy HH:mm')}</td>
                    <td>{payment.sale_receipt || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
