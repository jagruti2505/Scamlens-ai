// A printable report. Content comes only from report_data saved in MySQL.
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Printer } from 'lucide-react'
import { EmptyState, ErrorAlert, RiskBadge, SeverityBadge, Spinner } from '../components/ui'
import { api, errorMessage } from '../services/api'
import { formatDate, scanTypeLabel } from '../utils'

function Section({ title, items }) {
  if (!items?.length) return null
  return (
    <section className="mt-7 break-inside-avoid">
      <h2 className="mb-2 text-base font-semibold">{title}</h2>
      <ul className="list-disc space-y-1 pl-5 text-sm text-slate-300">{items.map((t, i) => <li key={i}>{t}</li>)}</ul>
    </section>
  )
}

export default function ReportView() {
  const { id } = useParams()
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [missing, setMissing] = useState(false)

  useEffect(() => {
    api.getReport(id).then(setReport).catch((err) => {
      if (err.response?.status === 404) setMissing(true)
      else setError(errorMessage(err))
    })
  }, [id])

  if (missing) return <div className="card"><EmptyState title="Report not found" action={<Link to="/reports" className="btn btn-primary">All reports</Link>}>It may have been deleted together with its scan.</EmptyState></div>
  if (error) return <ErrorAlert message={error} />
  if (!report) return <Spinner label="Loading report…" />

  const d = report.report_data
  const scan = d.scan
  return (
    <div>
      <div className="no-print mb-5 flex flex-wrap gap-2">
        <Link to="/reports" className="btn btn-ghost"><ArrowLeft className="size-4" />All reports</Link>
        <Link to={`/scans/${scan.id}`} className="btn btn-ghost">Open scan</Link>
        <button type="button" onClick={() => window.print()} className="btn btn-primary"><Printer className="size-4" />Print / Save as PDF</button>
      </div>

      <article className="print-area card mx-auto max-w-4xl p-6 sm:p-10 animate-rise">
        <header className="flex flex-col gap-4 border-b border-ink-700 pb-6 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">SCAMLENS AI · Risk report</p>
            <h1 className="mt-2 text-2xl font-semibold">{d.title}</h1>
            <p className="mt-1 text-sm text-mist">
              Report #{report.id} · generated {formatDate(d.generated_at)} · scan performed {formatDate(scan.created_at)}
            </p>
          </div>
          <div className="text-left sm:text-right">
            <div className="font-mono text-5xl font-semibold text-white">{scan.risk_score ?? 'N/A'}</div>
            <RiskBadge label={scan.risk_label} className="mt-2" />
          </div>
        </header>

        <section className="mt-6 grid gap-4 text-sm sm:grid-cols-2">
          <div><span className="text-mist">Scan type:</span> <span className="text-slate-200">{scanTypeLabel(scan.scan_type)}</span></div>
          <div><span className="text-mist">Status:</span> <span className="text-slate-200">{scan.status === 'completed' ? 'Completed' : 'Insufficient evidence'}</span></div>
          <div className="sm:col-span-2"><span className="text-mist">Input:</span> <span className="text-slate-200">{scan.input_summary}</span></div>
        </section>

        <section className="mt-6">
          <h2 className="mb-2 text-base font-semibold">Summary</h2>
          <p className="text-sm leading-relaxed text-slate-300">{scan.summary}</p>
          <p className="mt-2 text-xs text-slate-500">Scoring method: {scan.scoring_method}</p>
        </section>

        <section className="mt-7">
          <h2 className="mb-3 text-base font-semibold">Warning signs ({d.findings.length})</h2>
          {d.findings.length === 0 ? <p className="text-sm text-slate-400">No warning signs matched the built-in rules.</p> : (
            <ol className="space-y-3">
              {d.findings.map((f, i) => (
                <li key={i} className="break-inside-avoid rounded-xl border border-ink-700 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <SeverityBadge severity={f.severity} />
                    <span className="font-semibold text-white">{f.indicator}</span>
                    {f.strength && <span className="text-xs text-slate-500">evidence {f.strength} · weight {f.weight}</span>}
                  </div>
                  {f.evidence && <p className="mt-2 break-words font-mono text-xs text-slate-300">{f.evidence}</p>}
                  {f.explanation && <p className="mt-2 text-sm text-slate-300">{f.explanation}</p>}
                </li>
              ))}
            </ol>
          )}
        </section>

        <Section title="Recommendations" items={d.recommendations} />
        <Section title="Sources checked" items={d.sources_checked} />
        <Section title="Checks that could not be completed" items={d.unavailable_checks} />
        <Section title="Limitations" items={d.limitations} />

        <footer className="mt-8 border-t border-ink-700 pt-4 text-xs leading-relaxed text-slate-500">{d.disclaimer}</footer>
      </article>
    </div>
  )
}
