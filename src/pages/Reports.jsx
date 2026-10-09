// List of generated reports.
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileText } from 'lucide-react'
import { EmptyState, ErrorAlert, PageHeader, RiskBadge, Spinner } from '../components/ui'
import { api, errorMessage } from '../services/api'
import { formatDate, scanTypeLabel } from '../utils'

export default function Reports() {
  const [reports, setReports] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    setError('')
    api.listReports().then(setReports).catch((err) => setError(errorMessage(err)))
  }, [])
  useEffect(load, [load])

  return (
    <div>
      <PageHeader icon={FileText} title="Reports"
        subtitle='Printable reports built from stored scan data. Create one with the "Printable report" button on any scan result.' />
      <ErrorAlert message={error} onRetry={load} />
      {!reports && !error && <Spinner />}
      {reports && (
        reports.length === 0 ? (
          <div className="card">
            <EmptyState icon={FileText} title="No reports yet" action={<Link to="/history" className="btn btn-primary">Open scan history</Link>}>
              Open a scan and choose "Printable report" to generate one.
            </EmptyState>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {reports.map((r, i) => (
              <Link key={r.id} to={`/reports/${r.id}`} style={{ animationDelay: `${i * 30}ms` }}
                className="card group p-5 transition hover:-translate-y-0.5 hover:border-cyan-400/40 animate-rise">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-slate-500">Report #{r.id} · Scan #{r.scan_id}</span>
                  <span className="rounded-md bg-ink-800 px-2 py-0.5 text-[11px] uppercase tracking-wider text-mist">{r.report_type}</span>
                </div>
                <h3 className="mt-3 font-semibold text-white">{scanTypeLabel(r.scan_type)} scan</h3>
                <p className="mt-1 line-clamp-2 text-sm text-slate-400">{r.input_summary}</p>
                <div className="mt-4 flex items-center justify-between">
                  <RiskBadge label={r.risk_label} score={r.risk_score} />
                  <span className="text-xs text-slate-500">{formatDate(r.created_at)}</span>
                </div>
              </Link>
            ))}
          </div>
        )
      )}
    </div>
  )
}
