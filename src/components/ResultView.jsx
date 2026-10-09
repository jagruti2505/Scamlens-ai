// Displays one scan result: score, label, warning signs, evidence, sources, limitations and advice.
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Check, CheckCircle2, ClipboardCopy, FileText, Info, ListChecks, Loader2,
  SearchCheck, ShieldAlert, ShieldQuestion, Trash2, XCircle,
} from 'lucide-react'
import RiskGauge from './RiskGauge'
import { ErrorAlert, RiskBadge, SeverityBadge } from './ui'
import { api, errorMessage } from '../services/api'
import { copyText, formatDate, riskStyle, scanTypeLabel, summaryText } from '../utils'

function ListBlock({ icon: Icon, title, items, tone = 'text-mist', dot = 'bg-slate-400', empty }) {
  return (
    <div className="card p-5">
      <h3 className="section-title flex items-center gap-2"><Icon className={`size-4 ${tone}`} />{title}</h3>
      {items?.length ? (
        <ul className="space-y-2 text-sm text-slate-300">
          {items.map((item, i) => (
            <li key={i} className="flex gap-2.5"><span className={`mt-2 size-1.5 shrink-0 rounded-full ${dot}`} />{item}</li>
          ))}
        </ul>
      ) : <p className="text-sm text-slate-500">{empty}</p>}
    </div>
  )
}

function FindingCard({ finding, index }) {
  return (
    <article className="rounded-xl border border-ink-700 bg-ink-850/70 p-4 animate-rise" style={{ animationDelay: `${index * 50}ms` }}>
      <div className="flex flex-wrap items-center gap-2">
        <SeverityBadge severity={finding.severity} />
        <h4 className="font-semibold text-white">{finding.indicator}</h4>
        <span className="ml-auto text-xs text-slate-500">
          evidence: <span className="text-slate-300">{finding.strength}</span> · weight <span className="font-mono text-slate-300">{finding.weight}</span>
        </span>
      </div>
      <p className="mt-3 break-words rounded-lg border border-ink-700 bg-ink-950/60 px-3 py-2 font-mono text-[12.5px] leading-relaxed text-cyan-100/90">
        {finding.evidence}
      </p>
      <p className="mt-2.5 text-sm leading-relaxed text-slate-300">{finding.explanation}</p>
    </article>
  )
}

/**
 * compact=true is used right after a scan (shows the top findings and links to full details).
 * compact=false is the full detail page.
 */
export default function ResultView({ scan, compact = false, onDeleted }) {
  const navigate = useNavigate()
  const [copied, setCopied] = useState(false)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState('')
  const insufficient = scan.status === 'insufficient_evidence'
  const findings = compact ? scan.findings.slice(0, 3) : scan.findings
  const color = riskStyle(scan.risk_label).hex

  async function handleCopy() {
    setCopied(await copyText(summaryText(scan)))
    setTimeout(() => setCopied(false), 2000)
  }

  async function handleReport() {
    setBusy('report'); setError('')
    try {
      const report = await api.createReport(scan.id, 'detailed')
      navigate(`/reports/${report.id}`)
    } catch (err) { setError(errorMessage(err)) } finally { setBusy('') }
  }

  async function handleDelete() {
    if (!window.confirm(`Delete scan #${scan.id} and its reports? This cannot be undone.`)) return
    setBusy('delete'); setError('')
    try { await api.deleteScan(scan.id); onDeleted?.() } catch (err) { setError(errorMessage(err)); setBusy('') }
  }

  return (
    <section className="space-y-5 animate-rise" aria-live="polite">
      {/* Headline */}
      <div className="card relative overflow-hidden p-6">
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px" style={{ background: `linear-gradient(90deg, transparent, ${color}, transparent)` }} />
        <div className="flex flex-col gap-6 md:flex-row md:items-center">
          <RiskGauge score={scan.risk_score} label={scan.risk_label} />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <RiskBadge label={scan.risk_label} />
              <span className="rounded-full bg-ink-800 px-2.5 py-1 text-xs text-mist ring-1 ring-ink-600">{scanTypeLabel(scan.scan_type)}</span>
              <span className="font-mono text-xs text-slate-500">#{scan.id}</span>
            </div>
            <p className="mt-3 text-[15px] leading-relaxed text-slate-200">{scan.summary}</p>
            <p className="mt-2 truncate text-xs text-slate-500" title={scan.input_summary}>{scan.input_summary}</p>
            <p className="mt-1 text-xs text-slate-500">Scanned {formatDate(scan.created_at)}</p>
          </div>
        </div>
        <div className="mt-5 flex items-start gap-2.5 rounded-xl bg-ink-850 px-4 py-3 text-xs leading-relaxed text-mist ring-1 ring-ink-700">
          <Info className="mt-0.5 size-4 shrink-0 text-cyan-300" />
          <span>
            {insufficient
              ? 'There was not enough information to calculate a reliable score. '
              : 'This score is an estimated risk assessment based on the warning signs found — not a guaranteed probability of fraud. '}
            A low score does not guarantee that something is safe.
            <span className="mt-1 block text-slate-500">Method: {scan.scoring_method}</span>
          </span>
        </div>
        <div className="mt-5 flex flex-wrap gap-2 no-print">
          <Link to="/" className="btn btn-ghost"><ArrowLeft className="size-4" />Dashboard</Link>
          {compact && <Link to={`/scans/${scan.id}`} className="btn btn-ghost"><ListChecks className="size-4" />View detailed findings</Link>}
          <button type="button" onClick={handleCopy} className="btn btn-ghost">
            {copied ? <Check className="size-4 text-emerald-300" /> : <ClipboardCopy className="size-4" />}{copied ? 'Copied' : 'Copy summary'}
          </button>
          <button type="button" onClick={handleReport} disabled={!!busy} className="btn btn-primary">
            {busy === 'report' ? <Loader2 className="size-4 animate-spin" /> : <FileText className="size-4" />}Printable report
          </button>
          {!compact && (
            <button type="button" onClick={handleDelete} disabled={!!busy} className="btn btn-danger sm:ml-auto">
              {busy === 'delete' ? <Loader2 className="size-4 animate-spin" /> : <Trash2 className="size-4" />}Delete scan
            </button>
          )}
        </div>
        {error && <div className="mt-4"><ErrorAlert message={error} /></div>}
      </div>

      {/* Findings */}
      <div className="card p-5">
        <h3 className="section-title flex items-center gap-2">
          <ShieldAlert className="size-4 text-orange-300" />Warning signs found ({scan.findings.length})
        </h3>
        {scan.findings.length === 0 ? (
          <p className="flex items-center gap-2 text-sm text-slate-400">
            {insufficient ? <ShieldQuestion className="size-4" /> : <CheckCircle2 className="size-4 text-emerald-300" />}
            No warning signs matched the built-in rules{insufficient ? ' in the limited information provided' : ''}.
          </p>
        ) : (
          <div className="space-y-3">
            {findings.map((f, i) => <FindingCard key={f.id} finding={f} index={i} />)}
            {compact && scan.findings.length > 3 && (
              <Link to={`/scans/${scan.id}`} className="block rounded-xl border border-dashed border-ink-600 py-3 text-center text-sm text-cyan-300 hover:border-cyan-400/50">
                + {scan.findings.length - 3} more warning sign(s) — view detailed findings
              </Link>
            )}
          </div>
        )}
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <ListBlock icon={CheckCircle2} title="What you should do" items={scan.recommendations} tone="text-emerald-300" dot="bg-emerald-300" empty="No recommendations." />
        <ListBlock icon={SearchCheck} title="Sources actually checked" items={scan.sources_checked} tone="text-cyan-300" dot="bg-cyan-300" empty="None." />
        <ListBlock icon={XCircle} title="Checks that could not be completed" items={scan.unavailable_checks} tone="text-yellow-300" dot="bg-yellow-300" empty="All planned checks ran." />
        <ListBlock icon={Info} title="Limitations of this analysis" items={scan.limitations} tone="text-slate-400" dot="bg-slate-400" empty="None recorded." />
      </div>
    </section>
  )
}
