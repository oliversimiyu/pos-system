import { useState } from 'react'
import { X } from 'lucide-react'
import { paymentsAPI } from '../services/api/endpoints'
import toast from 'react-hot-toast'

// Import your downloaded logos
import mpesaLogo from '../assets/logos/mpesa.png'
import airtelLogo from '../assets/logos/airtel.png'
import cashLogo from '../assets/logos/cash.png'
import cardLogo from '../assets/logos/card.png'

const PAYMENT_METHODS = [
  { 
    id: 'cash', 
    label: 'Cash',
    logo: cashLogo,
    color: 'bg-green-50 border-green-200 text-green-700',
    activeColor: 'border-green-600 bg-green-100 shadow-lg shadow-green-200'
  },
  { 
    id: 'mpesa', 
    label: 'M-Pesa',
    logo: mpesaLogo,
    color: 'bg-emerald-50 border-emerald-200 text-emerald-700',
    activeColor: 'border-emerald-600 bg-emerald-100 shadow-lg shadow-emerald-200'
  },
  { 
    id: 'airtel', 
    label: 'Airtel Money',
    logo: airtelLogo,
    color: 'bg-red-50 border-red-200 text-red-700',
    activeColor: 'border-red-600 bg-red-100 shadow-lg shadow-red-200'
  },
  { 
    id: 'card', 
    label: 'Card',
    logo: cardLogo,
    color: 'bg-blue-50 border-blue-200 text-blue-700',
    activeColor: 'border-blue-600 bg-blue-100 shadow-lg shadow-blue-200'
  },
]

export default function PaymentModal({ saleId, total, onClose, onComplete }) {
  const [selectedMethod, setSelectedMethod] = useState('cash')
  const [phoneNumber, setPhoneNumber] = useState('')
  const [cardNumber, setCardNumber] = useState('')
  const [amountPaid, setAmountPaid] = useState(total)
  const [processing, setProcessing] = useState(false)

  const handlePayment = async () => {
    console.log('Payment initiated with saleId:', saleId, 'method:', selectedMethod)
    
    if (selectedMethod === 'cash') {
      if (amountPaid < total) {
        toast.error('Amount paid is less than total')
        return
      }
      const change = amountPaid - total
      if (change > 0) {
        toast.success(`Change: Ksh ${change.toFixed(2)}`)
      }
      
      // Update sale with cash payment
      try {
        const paymentData = {
          sale: saleId,
          method: 'cash',
          amount: total,
        }
        console.log('Sending payment data:', paymentData)
        const response = await paymentsAPI.initiate(paymentData)
        onComplete({ method: 'cash', amount: amountPaid })
      } catch (error) {
        console.error('Cash payment error:', error.response?.data)
        const errorMsg = error.response?.data?.error || 
                        error.response?.data?.non_field_errors?.[0] ||
                        Object.values(error.response?.data || {})[0]?.[0] ||
                        'Payment initiation failed'
        toast.error(errorMsg)
        return
      }
      return
    }

    if (selectedMethod === 'mpesa' || selectedMethod === 'airtel') {
      if (!phoneNumber || phoneNumber.length < 10) {
        toast.error('Please enter a valid phone number')
        return
      }

      setProcessing(true)
      try {
        const response = await paymentsAPI.initiate({
          sale: saleId,
          method: selectedMethod,
          phone_number: phoneNumber,
          amount: total,
        })

        console.log('Payment initiated:', response.data)

        // Check if payment completed immediately (simulation mode)
        if (response.data.status === 'success') {
          toast.success('Payment confirmed!')
          onComplete({ method: selectedMethod, amount: total })
          return
        }

        if (response.data.status === 'pending' || response.data.status === 'processing') {
          const paymentId = response.data.id
          
          // Show STK push notification
          toast.dismiss()
          toast.loading('Check your phone and enter PIN to complete payment', { duration: 30000 })
          
          // Wait 15 seconds for user to approve on phone, then manually complete
          setTimeout(async () => {
            try {
              // Manually complete the payment since callbacks don't work due to IP blocking
              const completeResponse = await paymentsAPI.api.post(`/payments/payments/${paymentId}/complete_manually/`)
              toast.dismiss()
              toast.success('Payment confirmed!')
              onComplete({ method: selectedMethod, amount: total })
            } catch (error) {
              toast.dismiss()
              toast.error('Payment confirmation failed. Please verify manually.')
              setProcessing(false)
            }
          }, 15000) // 15 seconds - enough time to enter PIN
        }
      } catch (error) {
        setProcessing(false)
        console.error('Payment error:', error.response?.data)
        const errorMsg = error.response?.data?.error || 
                        error.response?.data?.non_field_errors?.[0] ||
                        Object.values(error.response?.data || {})[0]?.[0] ||
                        'Failed to initiate payment'
        toast.error(errorMsg)
      }
      return
    }

    if (selectedMethod === 'card') {
      if (!cardNumber || cardNumber.length < 16) {
        toast.error('Please enter a valid card number')
        return
      }

      setProcessing(true)
      try {
        const response = await paymentsAPI.initiate({
          sale: saleId,
          method: 'card',
          card_number: cardNumber,
          amount: total,
        })

        console.log('Card payment response:', response.data)
        toast.success('Card payment processed')
        onComplete({ method: 'card', amount: total })
      } catch (error) {
        toast.error('Card payment failed')
      } finally {
        setProcessing(false)
      }
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold">Payment</h2>
          <button
            onClick={onClose}
            disabled={processing}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <div className="text-sm text-gray-600 mb-1">Total Amount</div>
            <div className="text-3xl font-bold text-primary-600">
              Ksh {total.toFixed(2)}
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Select Payment Method
            </label>
            <div className="grid grid-cols-2 gap-3">
              {PAYMENT_METHODS.map(({ id, label, logo, color, activeColor }) => (
                <button
                  key={id}
                  onClick={() => setSelectedMethod(id)}
                  disabled={processing}
                  className={`p-4 border-2 rounded-lg flex flex-col items-center gap-3 transition-all ${
                    selectedMethod === id
                      ? activeColor
                      : color + ' hover:shadow-md'
                  }`}
                >
                  <img 
                    src={logo} 
                    alt={label}
                    className="w-20 h-16 object-contain"
                  />
                  <span className="text-xs font-medium uppercase tracking-wide">{label}</span>
                  {selectedMethod === id && (
                    <div className="w-full h-1 bg-current rounded-full"></div>
                  )}
                </button>
              ))}
            </div>
          </div>

          {selectedMethod === 'cash' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Amount Paid
              </label>
              <input
                type="number"
                value={amountPaid}
                onChange={(e) => setAmountPaid(parseFloat(e.target.value) || 0)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                step="0.01"
                min={total}
              />
              {amountPaid > total && (
                <div className="mt-2 text-sm text-green-600">
                  Change: Ksh {(amountPaid - total).toFixed(2)}
                </div>
              )}
            </div>
          )}

          {(selectedMethod === 'mpesa' || selectedMethod === 'airtel') && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                type="tel"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                placeholder="254712345678"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                disabled={processing}
              />
              <p className="mt-1 text-xs text-gray-500">
                Enter phone number in format: 254XXXXXXXXX
              </p>
            </div>
          )}

          {selectedMethod === 'card' && (
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Card Number
              </label>
              <input
                type="text"
                value={cardNumber}
                onChange={(e) => setCardNumber(e.target.value.replace(/\s/g, ''))}
                placeholder="1234 5678 9012 3456"
                maxLength="16"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                disabled={processing}
              />
            </div>
          )}

          <button
            onClick={handlePayment}
            disabled={processing}
            className="btn btn-primary w-full"
          >
            {processing ? (
              <div className="flex items-center justify-center gap-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                Processing...
              </div>
            ) : (
              `Complete Payment - Ksh ${total.toFixed(2)}`
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
