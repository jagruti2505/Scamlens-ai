// Small display helpers shared across pages.

export const SCAN_TYPES = {
  message: { label: 'Message / Email', path: '/analyze/message' },
  url: { label: 'URL', path: '/analyze/url' },
  profile: { label: 'LinkedIn Profile', path: '/analyze/profile' },
  recruiter: { label: 'Recruiter & Job', path: '/analyze/recruiter' },
  company: { label: 'Company', path: '/analyze/company' },
  document: { label: 'Document', path: '/analyze/document' },
}

export const RISK_LABELS = [
  'Lower Observed Risk',
  'Caution',
  'Suspicious',
  'High Risk',
  'Very High Risk',
  'Insufficient Evidence',
]

const RISK_STYLE = {
  'Lower Observed Risk': { hex: '#34d399', chip: 'bg-emerald-400/10 text-emerald-300 ring-emerald-400/30' },
  Caution: { hex: '#facc15', chip: 'bg-yellow-400/10 text-yellow-200 ring-yellow-400/30' },
  Suspicious: { hex: '#fb923c', chip: 'bg-orange-400/10 text-orange-200 ring-orange-400/30' },
  'High Risk': { hex: '#f87171', chip: 'bg-red-400/10 text-red-200 ring-red-400/30' },
  'Very High Risk': { hex: '#f43f5e', chip: 'bg-rose-500/15 text-rose-200 ring-rose-500/40' },
  'Insufficient Evidence': { hex: '#94a3b8', chip: 'bg-slate-400/10 text-slate-300 ring-slate-400/30' },
}

export const riskStyle = (label) => RISK_STYLE[label] || RISK_STYLE['Insufficient Evidence']

export const SEVERITY_STYLE = {
  critical: 'bg-rose-500/15 text-rose-200 ring-rose-500/40',
  high: 'bg-red-400/10 text-red-200 ring-red-400/30',
  medium: 'bg-orange-400/10 text-orange-200 ring-orange-400/30',
  low: 'bg-sky-400/10 text-sky-200 ring-sky-400/30',
}

export const scanTypeLabel = (type) => SCAN_TYPES[type]?.label || type

export function formatDate(iso) {
  if (!iso) return '—'
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
}

export function summaryText(scan) {
  const lines = [
    `SCAMLENS AI — Scan #${scan.id} (${scanTypeLabel(scan.scan_type)})`,
    `Risk: ${scan.risk_label}${scan.risk_score != null ? ` (${scan.risk_score}/100)` : ''}`,
    `Scanned: ${formatDate(scan.created_at)}`,
    '',
    scan.summary || '',
  ]
  if (scan.findings?.length) {
    lines.push('', 'Warning signs:')
    scan.findings.forEach((f) => lines.push(`- [${f.severity}] ${f.indicator}`))
  }
  if (scan.recommendations?.length) {
    lines.push('', 'What to do:')
    scan.recommendations.forEach((r) => lines.push(`- ${r}`))
  }
  lines.push('', 'Note: this is an estimated risk assessment, not proof of fraud or of safety.')
  return lines.join('\n')
}

export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    const area = document.createElement('textarea')
    area.value = text
    area.style.position = 'fixed'
    area.style.opacity = '0'
    document.body.appendChild(area)
    area.select()
    const ok = document.execCommand('copy')
    area.remove()
    return ok
  }
}
