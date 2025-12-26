import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { usersAPI } from '../services/api/endpoints'
import { Plus, Search, Edit, Trash2, Shield, User as UserIcon } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

export default function Users() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [roleFilter, setRoleFilter] = useState('')

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async (params = {}) => {
    setLoading(true)
    try {
      const response = await usersAPI.getAll(params)
      setUsers(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to load users')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    const params = {}
    if (searchQuery) params.search = searchQuery
    if (roleFilter) params.role = roleFilter
    fetchUsers(params)
  }

  const handleDelete = async (id) => {
    if (id === currentUser.id) {
      toast.error('You cannot delete your own account')
      return
    }

    if (!confirm('Are you sure you want to delete this user?')) return

    try {
      await usersAPI.delete(id)
      toast.success('User deleted successfully')
      fetchUsers()
    } catch (error) {
      toast.error('Failed to delete user')
    }
  }

  const getRoleBadge = (role) => {
    return role === 'admin' ? 'badge-primary' : 'badge-secondary'
  }

  const getRoleIcon = (role) => {
    return role === 'admin' ? <Shield className="w-4 h-4" /> : <UserIcon className="w-4 h-4" />
  }

  if (currentUser?.role !== 'admin') {
    return (
      <div className="text-center py-12">
        <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-gray-800 mb-2">Access Denied</h2>
        <p className="text-gray-500">Only administrators can manage users.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">User Management</h1>
          <p className="text-gray-500">Manage cashiers and administrators</p>
        </div>
        <Link to="/users/new" className="btn btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Add User
        </Link>
      </div>

      {/* Filters */}
      <div className="card">
        <form onSubmit={handleSearch} className="flex gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search by name or username..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Roles</option>
            <option value="admin">Admin</option>
            <option value="cashier">Cashier</option>
          </select>
          <button type="submit" className="btn btn-secondary">
            Search
          </button>
        </form>
      </div>

      {/* Users Table */}
      <div className="card">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12">
            <UserIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No users found</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="font-medium">{user.username}</td>
                    <td>{`${user.first_name} ${user.last_name}`.trim() || '-'}</td>
                    <td>{user.email || '-'}</td>
                    <td>{user.phone_number || '-'}</td>
                    <td>
                      <span className={`badge ${getRoleBadge(user.role)} flex items-center gap-1 w-fit`}>
                        {getRoleIcon(user.role)}
                        {user.role}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${user.is_active ? 'badge-success' : 'badge-error'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td>{new Date(user.created_at).toLocaleDateString()}</td>
                    <td>
                      <div className="flex gap-2">
                        <Link
                          to={`/users/${user.id}/edit`}
                          className="text-primary-600 hover:text-primary-700"
                        >
                          <Edit className="w-4 h-4" />
                        </Link>
                        {user.id !== currentUser.id && (
                          <button
                            onClick={() => handleDelete(user.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
