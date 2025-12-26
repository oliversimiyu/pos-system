import axios from 'axios'
import toast from 'react-hot-toast'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    
    // Log full error for debugging
    console.error('API Error:', error.response?.data)
    
    // Extract error message from various possible formats
    let message = 'An error occurred'
    const data = error.response?.data
    
    if (data) {
      if (typeof data === 'string') {
        message = data
      } else if (data.error) {
        message = data.error
      } else if (data.detail) {
        message = data.detail
      } else if (data.message) {
        message = data.message
      } else if (data.items) {
        // Handle validation errors for nested fields like items
        message = JSON.stringify(data.items)
      } else {
        // Show first validation error
        const firstKey = Object.keys(data)[0]
        if (firstKey && data[firstKey]) {
          const errorValue = Array.isArray(data[firstKey]) ? data[firstKey][0] : data[firstKey]
          message = `${firstKey}: ${errorValue}`
        }
      }
    }
    
    toast.error(message)
    return Promise.reject(error)
  }
)

export default api
