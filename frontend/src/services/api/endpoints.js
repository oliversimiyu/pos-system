import api from './client'

export const authAPI = {
  login: (credentials) => api.post('/auth/login/', credentials),
  logout: () => api.post('/auth/logout/'),
  register: (userData) => api.post('/auth/register/', userData),
  getCurrentUser: () => api.get('/auth/me/'),
}

export const usersAPI = {
  getAll: (params) => api.get('/users/', { params }),
  getById: (id) => api.get(`/users/${id}/`),
  create: (data) => api.post('/users/', data),
  update: (id, data) => api.put(`/users/${id}/`, data),
  delete: (id) => api.delete(`/users/${id}/`),
}

export const productsAPI = {
  getAll: (params) => api.get('/products/', { params }),
  getById: (id) => api.get(`/products/${id}/`),
  getByBarcode: (barcode) => api.get(`/products/barcode/${barcode}/`),
  create: (data) => api.post('/products/', data),
  update: (id, data) => api.put(`/products/${id}/`, data),
  delete: (id) => api.delete(`/products/${id}/`),
  getLowStock: () => api.get('/products/low_stock/'),
  getCategories: () => api.get('/products/categories/'),
  createCategory: (data) => api.post('/products/categories/', data),
}

export const salesAPI = {
  getAll: (params) => api.get('/sales/sales/', { params }),
  getById: (id) => api.get(`/sales/sales/${id}/`),
  create: (data) => api.post('/sales/sales/', data),
  cancel: (id) => api.post(`/sales/sales/${id}/cancel/`),
  complete: (id) => api.post(`/sales/sales/${id}/complete/`),
  getToday: () => api.get('/sales/sales/today/'),
}

export const inventoryAPI = {
  getMovements: (params) => api.get('/inventory/movements/', { params }),
  createMovement: (data) => api.post('/inventory/movements/', data),
  getAlerts: (params) => api.get('/inventory/alerts/', { params }),
  getActiveAlerts: () => api.get('/inventory/alerts/active/'),
  resolveAlert: (id) => api.post(`/inventory/alerts/${id}/resolve/`),
  getCounts: (params) => api.get('/inventory/counts/', { params }),
  createCount: (data) => api.post('/inventory/counts/', data),
  addCountItem: (id, data) => api.post(`/inventory/counts/${id}/add_item/`, data),
  completeCount: (id) => api.post(`/inventory/counts/${id}/complete/`),
}

export const paymentsAPI = {
  getAll: (params) => api.get('/payments/payments/', { params }),
  initiate: (data) => api.post('/payments/payments/initiate/', data),
  verify: (id) => api.post(`/payments/payments/${id}/verify/`),
  getPending: () => api.get('/payments/payments/pending/'),
  getRefunds: (params) => api.get('/payments/refunds/', { params }),
  createRefund: (data) => api.post('/payments/refunds/', data),
  approveRefund: (id) => api.post(`/payments/refunds/${id}/approve/`),
}

export const reportsAPI = {
  getSalesReport: (params) => api.get('/reports/sales/', { params }),
  getInventoryReport: () => api.get('/reports/inventory/'),
  getProfitReport: (params) => api.get('/reports/profit/', { params }),
  getDashboard: () => api.get('/reports/dashboard/'),
}
