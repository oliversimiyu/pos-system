import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Receipt,
  Warehouse,
  CreditCard,
  BarChart3,
  Users,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard', roles: ['admin', 'cashier'] },
  { path: '/pos', icon: ShoppingCart, label: 'POS Checkout', roles: ['admin', 'cashier'] },
  { path: '/products', icon: Package, label: 'Products', roles: ['admin'] },
  { path: '/sales', icon: Receipt, label: 'Sales', roles: ['admin', 'cashier'] },
  { path: '/inventory', icon: Warehouse, label: 'Inventory', roles: ['admin'] },
  { path: '/payments', icon: CreditCard, label: 'Payments', roles: ['admin'] },
  { path: '/reports', icon: BarChart3, label: 'Reports', roles: ['admin'] },
  { path: '/users', icon: Users, label: 'Users', roles: ['admin'] },
]

export default function Sidebar() {
  const { user } = useAuth()

  const visibleNavItems = navItems.filter(item => 
    item.roles.includes(user?.role)
  )

  return (
    <aside className="fixed left-0 top-16 bottom-0 w-64 bg-white shadow-lg">
      <nav className="p-4">
        <ul className="space-y-2">
          {visibleNavItems.map(({ path, icon: Icon, label }) => (
            <li key={path}>
              <NavLink
                to={path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-600 font-medium'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  )
}
