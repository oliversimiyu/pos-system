import { useState, useEffect } from 'react'
import { inventoryAPI } from '../services/api/endpoints'
import { Package, AlertTriangle, TrendingUp, TrendingDown } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Inventory() {
  const [movements, setMovements] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('movements')

  useEffect(() => {
    fetchMovements()
    fetchAlerts()
  }, [])

  const fetchMovements = async () => {
    try {
      const response = await inventoryAPI.getMovements({ limit: 50 })
      setMovements(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to load stock movements')
    } finally {
      setLoading(false)
    }
  }

  const fetchAlerts = async () => {
    try {
      const response = await inventoryAPI.getActiveAlerts()
      setAlerts(response.data.results || response.data)
    } catch (error) {
      console.error('Failed to load alerts')
    }
  }

  const handleResolveAlert = async (id) => {
    try {
      await inventoryAPI.resolveAlert(id)
      toast.success('Alert resolved')
      fetchAlerts()
    } catch (error) {
      toast.error('Failed to resolve alert')
    }
  }

  const getMovementIcon = (type) => {
    return type === 'IN' ? (
      <TrendingUp className="w-4 h-4 text-green-600" />
    ) : (
      <TrendingDown className="w-4 h-4 text-red-600" />
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Inventory Management</h1>

      {/* Tabs */}
      <div className="flex gap-4 mb-6 border-b">
        <button
          onClick={() => setActiveTab('movements')}
          className={`pb-3 px-4 font-medium ${
            activeTab === 'movements'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Stock Movements
        </button>
        <button
          onClick={() => setActiveTab('alerts')}
          className={`pb-3 px-4 font-medium ${
            activeTab === 'alerts'
              ? 'border-b-2 border-primary-600 text-primary-600'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Stock Alerts ({alerts.length})
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <>
          {activeTab === 'movements' && (
            <div className="card overflow-hidden">
              <div className="overflow-x-auto">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Type</th>
                      <th>Product</th>
                      <th>Quantity</th>
                      <th>Reason</th>
                      <th>Date</th>
                      <th>User</th>
                    </tr>
                  </thead>
                  <tbody>
                    {movements.map((movement) => (
                      <tr key={movement.id}>
                        <td>
                          <div className="flex items-center gap-2">
                            {getMovementIcon(movement.movement_type)}
                            <span
                              className={`font-medium ${
                                movement.movement_type === 'IN'
                                  ? 'text-green-600'
                                  : 'text-red-600'
                              }`}
                            >
                              {movement.movement_type === 'IN' ? 'Stock In' : 'Stock Out'}
                            </span>
                          </div>
                        </td>
                        <td className="font-medium">{movement.product_name}</td>
                        <td>{movement.quantity}</td>
                        <td>{movement.reason || '-'}</td>
                        <td>{new Date(movement.created_at).toLocaleString()}</td>
                        <td>{movement.created_by_name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div className="space-y-4">
              {alerts.length === 0 ? (
                <div className="card text-center py-12 text-gray-400">
                  <Package className="w-16 h-16 mx-auto mb-3 opacity-50" />
                  <p>No active alerts</p>
                </div>
              ) : (
                alerts.map((alert) => (
                  <div key={alert.id} className="card bg-red-50 border-red-200">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <AlertTriangle className="w-5 h-5 text-red-600 mt-1" />
                        <div>
                          <h3 className="font-semibold text-gray-900">
                            {alert.product_name}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            Current Stock: {alert.current_stock} | Threshold:{' '}
                            {alert.threshold}
                          </p>
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(alert.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      {!alert.resolved && (
                        <button
                          onClick={() => handleResolveAlert(alert.id)}
                          className="btn btn-sm btn-secondary"
                        >
                          Resolve
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
