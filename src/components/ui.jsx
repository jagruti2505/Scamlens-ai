// Small reusable building blocks used by every page.
import { AlertTriangle, Inbox, Loader2, RefreshCw } from 'lucide-react'
import { riskStyle, SEVERITY_STYLE } from '../utils'

export function PageHeader({ icon: Icon, title, subtitle, actions }) {
  return (
    <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between animate-rise">
      <div className="flex items-start gap-3.5">
        {Icon && (
          <div className="mt-0.5 grid size-11 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-blue-500/25 to-cyan-400/10 ring-1 ring-cyan-400/25">
            <Icon className="size-5 text-cyan-300" />
          </div>
        )}
        <div>
          <h1 className="text-2xl font-semibold sm:text-[1.7rem]">{title}</h1>
          {subtitle && <p className="mt-1 max-w-2xl text-sm text-mist">{subtitle}</p>}
        </div>
      </div>
      {actions && <div className="flex flex-wrap gap-2 no-print">{actions}</div>}
    </div>
  )
}

export function Field({ label, hint, optional, children }) {
  return (
    <label className="block">
      <span className="label-text">
        {label}
        {optional && <span className="ml-1.5 text-xs font-normal text-slate-500">optional</span>}
      </span>
      {children}
      {hint && <span className="mt-1.5 block text-xs text-slate-500">{hint}</span>}
    </label>
  )
}

export function Spinner({ label = 'Loading…' }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-mist">
      <Loader2 className="size-5 animate-spin text-cyan-300" />
      <span className="text-sm">{label}</span>
    </div>
  )
}

export function ErrorAlert({ message, onRetry }) {
  if (!message) return null
  return (
    <div role="alert" className="flex items-start gap-3 rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-100 animate-rise">
      <AlertTriangle className="mt-0.5 size-4 shrink-0 text-rose-300" />
      <div className="flex-1">{message}</div>
      {onRetry && (
        <button type="button" onClick={onRetry} className="inline-flex items-center gap-1 text-rose-200 hover:text-white">
          <RefreshCw className="size-3.5" /> Retry
        </button>
      )}
    </div>
  )
}

export function EmptyState({ icon: Icon = Inbox, title, children, action }) {
  return (
    <div className="flex flex-col items-center px-6 py-14 text-center">
      <div className="mb-4 grid size-14 place-items-center rounded-2xl bg-ink-800 ring-1 ring-ink-600">
        <Icon className="size-6 text-mist" />
      </div>
      <h3 className="text-base font-semibold">{title}</h3>
      {children && <p className="mt-1.5 max-w-md text-sm text-mist">{children}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}

export function RiskBadge({ label, score, className = '' }) {
  const style = riskStyle(label)
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${style.chip} ${className}`}>
      <span className="size-1.5 rounded-full" style={{ background: style.hex }} />
      {label}
      {score != null && <span className="font-mono opacity-80">{score}</span>}
    </span>
  )
}

export function SeverityBadge({ severity }) {
  return (
    <span className={`rounded-md px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wider ring-1 ${SEVERITY_STYLE[severity] || SEVERITY_STYLE.low}`}>
      {severity}
    </span>
  )
}
