export default function CardLogo({ className = "w-16 h-16" }) {
  return (
    <svg className={className} viewBox="0 0 120 40" fill="none" xmlns="http://www.w3.org/2000/svg">
      {/* Card background - gradient */}
      <defs>
        <linearGradient id="cardGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{stopColor: '#3B82F6', stopOpacity: 1}} />
          <stop offset="100%" style={{stopColor: '#1D4ED8', stopOpacity: 1}} />
        </linearGradient>
      </defs>
      <rect width="120" height="40" rx="4" fill="url(#cardGradient)"/>
      
      {/* Card chip */}
      <rect x="10" y="12" width="16" height="12" rx="2" fill="#FCD34D"/>
      
      {/* Card text */}
      <text x="90" y="25" fontFamily="Arial, sans-serif" fontSize="12" fontWeight="bold" fill="white" textAnchor="end">
        VISA
      </text>
    </svg>
  )
}
