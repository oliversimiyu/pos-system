export default function MpesaLogo({ className = "w-16 h-16" }) {
  return (
    <svg className={className} viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* M-PESA background */}
      <rect width="120" height="40" rx="4" fill="#00A850"/>
      
      {/* M-PESA Text */}
      <text x="60" y="25" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" fill="white" textAnchor="middle">
        M-PESA
      </text>
    </svg>
  )
}
