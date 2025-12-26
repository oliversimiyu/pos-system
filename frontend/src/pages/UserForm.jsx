import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { usersAPI } from '../services/api/endpoints'
import { Save, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

export default function UserForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user: currentUser } = useAuth()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    role: 'cashier',
    is_active: true,
  })

  useEffect(() => {
    if (id) fetchUser()
  }, [id])

  const fetchUser = async () => {
    setLoading(true)
    try {
      const response = await usersAPI.getById(id)
      const userData = response.data
      setFormData({
        username: userData.username,
        email: userData.email || '',
        password: '', // Don't populate password
        first_name: userData.first_name || '',
        last_name: userData.last_name || '',
        phone_number: userData.phone_number || '',
        role: userData.role,
        is_active: userData.is_active,
      })
    } catch (error) {
      toast.error('Failed to load user')
      navigate('/users')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      const submitData = { ...formData }
      
      // Remove password field if editing and password is empty
      if (id && !submitData.password) {
        delete submitData.password
      }

      // Validate password for new users
      if (!id && !submitData.password) {
        toast.error('Password is required for new users')
        setLoading(false)
        return
      }

      if (id) {
        await usersAPI.update(id, submitData)
        toast.success('User updated successfully')
      } else {
        await usersAPI.create(submitData)
        toast.success('User created successfully')
      }
      navigate('/users')
    } catch (error) {
      const errorMsg = error.response?.data?.username?.[0] || 
                      error.response?.data?.email?.[0] ||
                      error.response?.data?.password?.[0] ||
                      'Failed to save user'
      toast.error(errorMsg)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  if (currentUser?.role !== 'admin') {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Access Denied</h2>
        <p className="text-gray-500">Only administrators can manage users.</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/users')}
          className="text-gray-600 hover:text-gray-800"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            {id ? 'Edit User' : 'Add New User'}
          </h1>
          <p className="text-gray-500">
            {id ? 'Update user information' : 'Create a new user account'}
          </p>
        </div>
      </div>

      {/* Form */}
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Username */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              className="input w-full"
              placeholder="johndoe"
            />
          </div>

          {/* Name */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                First Name
              </label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                className="input w-full"
                placeholder="John"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Last Name
              </label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                className="input w-full"
                placeholder="Doe"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="input w-full"
              placeholder="john@example.com"
            />
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number
            </label>
            <input
              type="tel"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              className="input w-full"
              placeholder="+254712345678"
            />
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password {!id && <span className="text-red-500">*</span>}
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required={!id}
              className="input w-full"
              placeholder={id ? 'Leave blank to keep current password' : 'Min 8 characters'}
              minLength={8}
            />
            {id && (
              <p className="text-sm text-gray-500 mt-1">
                Leave blank to keep the current password
              </p>
            )}
          </div>

          {/* Role */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Role <span className="text-red-500">*</span>
            </label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
              className="input w-full"
            >
              <option value="cashier">Cashier</option>
              <option value="admin">Admin</option>
            </select>
            <p className="text-sm text-gray-500 mt-1">
              Admins have full access. Cashiers can only access POS and view their sales.
            </p>
          </div>

          {/* Active Status */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
              Active (user can log in)
            </label>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {loading ? 'Saving...' : id ? 'Update User' : 'Create User'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/users')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
