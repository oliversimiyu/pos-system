import { useState } from 'react'
import { X, Smartphone, CreditCard, Banknote } from 'lucide-react'
import { paymentsAPI } from '../services/api/endpoints'
import toast from 'react-hot-toast'

const PAYMENT_METHODS = [
  { id: 'cash', label: 'Cash', icon: Banknote },
  { id: 'mpesa', label: 'M-Pesa', icon: Smartphone },
  { id: 'airtel', label: 'Airtel Money', icon: Smartphone },
  { id: 'card', label: 'Card', icon: CreditCard },
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
          toast.loading('Payment initiated. Waiting for confirmation...')
          // Poll for payment status
          const checkStatus = setInterval(async () => {
            try {
              const verifyResponse = await paymentsAPI.verify(response.data.id)
              console.log('Payment status:', verifyResponse.data.status)
              if (verifyResponse.data.status === 'success') {
                clearInterval(checkStatus)
                toast.dismiss()
                toast.success('Payment confirmed!')
                onComplete({ method: selectedMethod, amount: total })
              } else if (verifyResponse.data.status === 'failed') {
                clearInterval(checkStatus)
                toast.dismiss()
                toast.error('Payment failed')
                setProcessing(false)
              }
            } catch (error) {
              clearInterval(checkStatus)
              setProcessing(false)
            }
          }, 3000)

          // Stop polling after 2 minutes
          setTimeout(() => {
            clearInterval(checkStatus)
            setProcessing(false)
            toast.dismiss()
            toast.error('Payment timeout')
          }, 120000)
        }
      } catch (error) {
        setProcessing(false)
        toast.error('Failed to initiate payment')
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
              {PAYMENT_METHODS.map(({ id, label, icon: Icon }) => (
                <button
                  key={id}
                  onClick={() => setSelectedMethod(id)}
                  disabled={processing}
                  className={`p-4 border-2 rounded-lg flex flex-col items-center gap-2 transition-colors ${
                    selectedMethod === id
                      ? 'border-primary-600 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-6 h-6" />
                  <span className="text-sm font-medium">{label}</span>
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
