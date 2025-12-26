import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { salesAPI } from '../services/api/endpoints'
import { Eye, Search, Calendar } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

export default function Sales() {
  const [sales, setSales] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  useEffect(() => {
    fetchSales()
  }, [])

  const fetchSales = async (params = {}) => {
    setLoading(true)
    try {
      const response = await salesAPI.getAll(params)
      setSales(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to load sales')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    const params = {}
    if (searchQuery) params.search = searchQuery
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    fetchSales(params)
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      completed: 'badge-success',
      cancelled: 'badge-error',
    }
    return `badge ${badges[status] || ''}`
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Sales</h1>
      </div>

      <div className="card mb-6">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by receipt number or customer..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="Start Date"
              />
            </div>
            <div>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                placeholder="End Date"
              />
            </div>
          </div>
          <button type="submit" className="btn btn-secondary">
            Apply Filters
          </button>
        </form>
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
                  <th>Receipt #</th>
                  <th>Date</th>
                  <th>Items</th>
                  <th>Total</th>
                  <th>Payment Method</th>
                  <th>Status</th>
                  <th>Cashier</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sales.map((sale) => (
                  <tr key={sale.id}>
                    <td className="font-mono font-medium">{sale.receipt_number}</td>
                    <td>{format(new Date(sale.created_at), 'MMM dd, yyyy HH:mm')}</td>
                    <td>{sale.items?.length || 0}</td>
                    <td className="font-semibold">Ksh {sale.total_amount}</td>
                    <td>
                      <span className="badge badge-secondary">
                        {sale.payment_method}
                      </span>
                    </td>
                    <td>
                      <span className={getStatusBadge(sale.status)}>
                        {sale.status}
                      </span>
                    </td>
                    <td>{sale.cashier_name}</td>
                    <td>
                      <Link
                        to={`/sales/${sale.id}`}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        <Eye className="w-4 h-4" />
                      </Link>
                    </td>
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
