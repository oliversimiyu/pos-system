export default function CashLogo({ className = "w-16 h-16" }) {
  return (
    <svg className={className} viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Cash background */}
      <rect width="120" height="40" rx="4" fill="#10B981"/>
      
      {/* Dollar sign */}
      <text x="60" y="28" fontFamily="Arial, sans-serif" fontSize="24" fontWeight="bold" fill="white" textAnchor="middle">
        💵
      </text>
    </svg>
  )
}
