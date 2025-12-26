import { useState, useRef, useEffect } from 'react'
import { productsAPI, salesAPI } from '../services/api/endpoints'
import { Search, Scan, ShoppingCart, Trash2, Plus, Minus, X } from 'lucide-react'
import toast from 'react-hot-toast'
import PaymentModal from '../components/PaymentModal'

export default function POSCheckout() {
  const [barcode, setBarcode] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [products, setProducts] = useState([])
  const [cart, setCart] = useState([])
  const [loading, setLoading] = useState(false)
  const [showPayment, setShowPayment] = useState(false)
  const [cartTotal, setCartTotal] = useState(0)
  const barcodeInputRef = useRef(null)

  useEffect(() => {
    // Auto-focus barcode scanner input
    barcodeInputRef.current?.focus()
  }, [cart])

  useEffect(() => {
    // Calculate cart total
    const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0)
    setCartTotal(total)
  }, [cart])

  const handleBarcodeSubmit = async (e) => {
    e.preventDefault()
    if (!barcode.trim()) return

    setLoading(true)
    try {
      const response = await productsAPI.getByBarcode(barcode.trim())
      const product = response.data
      addToCart(product)
      setBarcode('')
      toast.success(`Added ${product.name} to cart`)
    } catch (error) {
      toast.error('Product not found')
    } finally {
      setLoading(false)
    }
  }

  const handleProductSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setLoading(true)
    try {
      const response = await productsAPI.getAll({ search: searchQuery })
      setProducts(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to search products')
    } finally {
      setLoading(false)
    }
  }

  const addToCart = (product) => {
    if (product.stock_quantity <= 0) {
      toast.error('Product out of stock')
      return
    }

    const existing = cart.find((item) => item.id === product.id)
    if (existing) {
      if (existing.quantity >= product.stock_quantity) {
        toast.error('Insufficient stock')
        return
      }
      updateQuantity(product.id, existing.quantity + 1)
    } else {
      setCart([...cart, { ...product, quantity: 1 }])
    }
    setProducts([])
    setSearchQuery('')
  }

  const updateQuantity = (productId, newQuantity) => {
    const product = cart.find((item) => item.id === productId)
    if (newQuantity > product.stock_quantity) {
      toast.error('Insufficient stock')
      return
    }
    if (newQuantity <= 0) {
      removeFromCart(productId)
      return
    }
    setCart(cart.map((item) =>
      item.id === productId ? { ...item, quantity: newQuantity } : item
    ))
  }

  const removeFromCart = (productId) => {
    setCart(cart.filter((item) => item.id !== productId))
  }

  const clearCart = () => {
    setCart([])
    setProducts([])
    setSearchQuery('')
    setBarcode('')
  }

  const handleCheckout = () => {
    if (cart.length === 0) {
      toast.error('Cart is empty')
      return
    }
    setShowPayment(true)
  }

  const handlePaymentComplete = async (paymentData) => {
    try {
      const saleData = {
        items: cart.map((item) => ({
          product: item.id,
          quantity: item.quantity,
          price: item.price,
        })),
        payment_method: paymentData.method,
        amount_paid: paymentData.amount,
      }

      const response = await salesAPI.create(saleData)
      toast.success(`Sale completed! Receipt #${response.data.receipt_number}`)
      clearCart()
      setShowPayment(false)
    } catch (error) {
      toast.error('Failed to complete sale')
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Product Search & Add Section */}
      <div className="lg:col-span-2 space-y-6">
        {/* Barcode Scanner Input */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Scan className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold">Barcode Scanner</h2>
          </div>
          <form onSubmit={handleBarcodeSubmit} className="flex gap-2">
            <input
              ref={barcodeInputRef}
              type="text"
              value={barcode}
              onChange={(e) => setBarcode(e.target.value)}
              placeholder="Scan or enter barcode..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <button type="submit" className="btn btn-primary" disabled={loading}>
              Add
            </button>
          </form>
        </div>

        {/* Manual Product Search */}
        <div className="card">
          <div className="flex items-center gap-2 mb-4">
            <Search className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold">Search Products</h2>
          </div>
          <form onSubmit={handleProductSearch} className="flex gap-2 mb-4">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by name, SKU, or category..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              disabled={loading}
            />
            <button type="submit" className="btn btn-secondary" disabled={loading}>
              Search
            </button>
          </form>

          {/* Search Results */}
          {products.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {products.map((product) => (
                <div
                  key={product.id}
                  className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 cursor-pointer"
                  onClick={() => addToCart(product)}
                >
                  <h3 className="font-medium text-gray-900">{product.name}</h3>
                  <p className="text-sm text-gray-600">{product.category_name}</p>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-lg font-bold text-primary-600">
                      Ksh {product.price}
                    </span>
                    <span className="text-sm text-gray-500">
                      Stock: {product.stock_quantity}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Shopping Cart */}
      <div className="lg:col-span-1">
        <div className="card sticky top-24">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-primary-600" />
              <h2 className="text-lg font-semibold">Cart ({cart.length})</h2>
            </div>
            {cart.length > 0 && (
              <button
                onClick={clearCart}
                className="text-sm text-red-600 hover:text-red-700"
              >
                Clear All
              </button>
            )}
          </div>

          {cart.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <ShoppingCart className="w-16 h-16 mx-auto mb-3 opacity-50" />
              <p>Cart is empty</p>
              <p className="text-sm">Scan or search to add products</p>
            </div>
          ) : (
            <>
              <div className="space-y-3 max-h-96 overflow-y-auto mb-4">
                {cart.map((item) => (
                  <div key={item.id} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900 text-sm">
                          {item.name}
                        </h3>
                        <p className="text-xs text-gray-600">
                          Ksh {item.price} each
                        </p>
                      </div>
                      <button
                        onClick={() => removeFromCart(item.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity - 1)}
                          className="p-1 rounded bg-white border border-gray-300 hover:bg-gray-50"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="w-8 text-center font-medium">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.id, item.quantity + 1)}
                          className="p-1 rounded bg-white border border-gray-300 hover:bg-gray-50"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>
                      <span className="font-semibold text-primary-600">
                        Ksh {(item.price * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="border-t pt-4">
                <div className="flex justify-between items-center mb-4">
                  <span className="text-lg font-semibold">Total</span>
                  <span className="text-2xl font-bold text-primary-600">
                    Ksh {cartTotal.toFixed(2)}
                  </span>
                </div>
                <button onClick={handleCheckout} className="btn btn-primary w-full">
                  Proceed to Payment
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Payment Modal */}
      {showPayment && (
        <PaymentModal
          total={cartTotal}
          onClose={() => setShowPayment(false)}
          onComplete={handlePaymentComplete}
        />
      )}
    </div>
  )
}
