// Circular gauge showing the 0-100 risk score (or "N/A" when evidence is insufficient).
import { riskStyle } from '../utils'

export default function RiskGauge({ score, label, size = 148 }) {
  const stroke = 11
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const arc = circumference * 0.75 // 270° gauge
  const value = score == null ? 0 : Math.max(0, Math.min(100, score))
  const color = riskStyle(label).hex

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="rotate-[135deg]">
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--color-ink-700)"
          strokeWidth={stroke} strokeDasharray={`${arc} ${circumference}`} strokeLinecap="round" />
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={color} strokeWidth={stroke}
          strokeDasharray={`${(arc * value) / 100} ${circumference}`} strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.9s cubic-bezier(.2,.7,.2,1)', filter: `drop-shadow(0 0 6px ${color}66)` }} />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-4xl font-semibold text-white">{score == null ? 'N/A' : score}</span>
        <span className="mt-0.5 text-[11px] uppercase tracking-[0.18em] text-mist">{score == null ? 'no score' : 'of 100'}</span>
      </div>
    </div>
  )
}
