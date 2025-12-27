export default function AirtelLogo({ className = "w-16 h-16" }) {
  return (
    <svg className={className} viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Airtel background */}
      <rect width="120" height="40" rx="4" fill="#ED1C24"/>
      
      {/* Airtel Text */}
      <text x="60" y="18" fontFamily="Arial, sans-serif" fontSize="14" fontWeight="bold" fill="white" textAnchor="middle">
        airtel
      </text>
      <text x="60" y="32" fontFamily="Arial, sans-serif" fontSize="10" fontWeight="normal" fill="white" textAnchor="middle">
        MONEY
      </text>
    </svg>
  )
}
