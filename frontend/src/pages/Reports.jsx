import { useState, useEffect } from 'react'
import { reportsAPI } from '../services/api/endpoints'
import { Download, Calendar } from 'lucide-react'
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'

const COLORS = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

export default function Reports() {
  const [activeTab, setActiveTab] = useState('sales')
  const [period, setPeriod] = useState('today')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const [salesData, setSalesData] = useState(null)
  const [inventoryData, setInventoryData] = useState(null)
  const [profitData, setProfitData] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchReports()
  }, [activeTab, period])

  const fetchReports = async () => {
    setLoading(true)
    try {
      const params = { period }
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate

      if (activeTab === 'sales') {
        const response = await reportsAPI.getSalesReport(params)
        setSalesData(response.data)
      } else if (activeTab === 'inventory') {
        const response = await reportsAPI.getInventoryReport()
        setInventoryData(response.data)
      } else if (activeTab === 'profit') {
        const response = await reportsAPI.getProfitReport(params)
        setProfitData(response.data)
      }
    } catch (error) {
      toast.error('Failed to load report')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    toast.success('Export feature coming soon!')
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Reports & Analytics</h1>
        <button onClick={handleExport} className="btn btn-secondary flex items-center gap-2">
          <Download className="w-4 h-4" />
          Export Report
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b">
        <button
          onClick={() => setActiveTab('sales')}
          className={`pb-3 px-4 font-medium ${
            activeTab === 'sales'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Sales Report
        </button>
        <button
          onClick={() => setActiveTab('inventory')}
          className={`pb-3 px-4 font-medium ${
            activeTab === 'inventory'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Inventory Report
        </button>
        <button
          onClick={() => setActiveTab('profit')}
          className={`pb-3 px-4 font-medium ${
            activeTab === 'profit'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Profit Analysis
        </button>
      </div>

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Period
            </label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="year">This Year</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
          {period === 'custom' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </>
          )}
          <div className="flex items-end">
            <button onClick={fetchReports} className="btn btn-primary w-full">
              Generate Report
            </button>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {activeTab === 'sales' && salesData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card">
                  <p className="text-sm text-gray-600">Total Sales</p>
                  <p className="text-2xl font-bold text-primary-600">
                    Ksh {salesData.total_sales || '0.00'}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-600">Transactions</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {salesData.total_transactions || 0}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-600">Average Sale</p>
                  <p className="text-2xl font-bold text-gray-900">
                    Ksh {salesData.average_sale || '0.00'}
                  </p>
                </div>
              </div>

              {salesData.chart_data && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Sales Trend</h3>
                  <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={salesData.chart_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="sales" stroke="#4F46E5" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {activeTab === 'inventory' && inventoryData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card">
                  <p className="text-sm text-gray-600">Total Products</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {inventoryData.total_products || 0}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-600">Low Stock Items</p>
                  <p className="text-2xl font-bold text-red-600">
                    {inventoryData.low_stock_count || 0}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-600">Total Stock Value</p>
                  <p className="text-2xl font-bold text-primary-600">
                    Ksh {inventoryData.total_value || '0.00'}
                  </p>
                </div>
              </div>

              {inventoryData.category_distribution && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Stock by Category</h3>
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={inventoryData.category_distribution}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={150}
                        label
                      >
                        {inventoryData.category_distribution.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {activeTab === 'profit' && profitData && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="card">
                  <p className="text-sm text-gray-600">Total Revenue</p>
                  <p className="text-2xl font-bold text-primary-600">
                    Ksh {profitData.total_revenue || '0.00'}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-600">Total Cost</p>
                  <p className="text-2xl font-bold text-gray-900">
                    Ksh {profitData.total_cost || '0.00'}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-600">Gross Profit</p>
                  <p className="text-2xl font-bold text-green-600">
                    Ksh {profitData.gross_profit || '0.00'}
                  </p>
                </div>
                <div className="card">
                  <p className="text-sm text-gray-600">Profit Margin</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {profitData.profit_margin || '0'}%
                  </p>
                </div>
              </div>

              {profitData.chart_data && (
                <div className="card">
                  <h3 className="text-lg font-semibold mb-4">Profit Trend</h3>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={profitData.chart_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="revenue" fill="#4F46E5" />
                      <Bar dataKey="cost" fill="#EF4444" />
                      <Bar dataKey="profit" fill="#10B981" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
