// Searchable, filterable, sortable list of all scans stored in MySQL.
import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, History, Search, Trash2 } from 'lucide-react'
import { EmptyState, ErrorAlert, PageHeader, RiskBadge, Spinner } from '../components/ui'
import { api, errorMessage } from '../services/api'
import { formatDate, RISK_LABELS, SCAN_TYPES, scanTypeLabel } from '../utils'

const PAGE_SIZE = 20

export default function ScanHistory() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [debounced, setDebounced] = useState('')
  const [scanType, setScanType] = useState('')
  const [riskLabel, setRiskLabel] = useState('')
  const [sort, setSort] = useState('newest')
  const [page, setPage] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    const t = setTimeout(() => { setDebounced(search.trim()); setPage(0) }, 300)
    return () => clearTimeout(t)
  }, [search])

  const load = useCallback(() => {
    setError('')
    const params = { sort, limit: PAGE_SIZE, offset: page * PAGE_SIZE }
    if (debounced) params.search = debounced
    if (scanType) params.scan_type = scanType
    if (riskLabel) params.risk_label = riskLabel
    api.listScans(params).then(setResult).catch((err) => setError(errorMessage(err)))
  }, [debounced, scanType, riskLabel, sort, page])
  useEffect(load, [load])

  async function remove(e, scan) {
    e.stopPropagation()
    if (!window.confirm(`Delete scan #${scan.id}? Its reports will also be deleted.`)) return
    try { await api.deleteScan(scan.id); load() } catch (err) { setError(errorMessage(err)) }
  }

  const filtersActive = debounced || scanType || riskLabel
  const pages = result ? Math.max(1, Math.ceil(result.total / PAGE_SIZE)) : 1

  return (
    <div>
      <PageHeader icon={History} title="Scan History"
        subtitle="All scans saved in the local MySQL database. History is shared by everyone using this installation." />

      <div className="card mb-5 grid gap-3 p-4 md:grid-cols-[minmax(0,1fr)_170px_190px_170px]">
        <label className="relative">
          <span className="sr-only">Search</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-500" />
          <input className="input pl-9" placeholder="Search by ID, domain, company…" value={search} onChange={(e) => setSearch(e.target.value)} />
        </label>
        <select className="input" value={scanType} onChange={(e) => { setScanType(e.target.value); setPage(0) }} aria-label="Scan type">
          <option value="">All types</option>
          {Object.entries(SCAN_TYPES).map(([k, v]) => <option key={k} value={k}>{v.label}</option>)}
        </select>
        <select className="input" value={riskLabel} onChange={(e) => { setRiskLabel(e.target.value); setPage(0) }} aria-label="Risk label">
          <option value="">All risk levels</option>
          {RISK_LABELS.map((l) => <option key={l} value={l}>{l}</option>)}
        </select>
        <select className="input" value={sort} onChange={(e) => { setSort(e.target.value); setPage(0) }} aria-label="Sort">
          <option value="newest">Newest first</option>
          <option value="oldest">Oldest first</option>
          <option value="score_high">Highest risk</option>
          <option value="score_low">Lowest risk</option>
        </select>
      </div>

      <ErrorAlert message={error} onRetry={load} />
      {!result && !error && <Spinner />}
      {result && (
        <div className="card overflow-hidden">
          {result.items.length === 0 ? (
            <EmptyState icon={History} title={filtersActive ? 'No scans match these filters' : 'No scans yet'}
              action={!filtersActive && <Link to="/analyze/message" className="btn btn-primary">Run a scan</Link>}>
              {filtersActive ? 'Try a different search or clear the filters.' : 'Your scan history will appear here.'}
            </EmptyState>
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <thead className="border-b border-ink-700 text-xs uppercase tracking-wider text-mist">
                    <tr>
                      <th className="px-5 py-3 font-medium">Scan ID</th>
                      <th className="px-3 py-3 font-medium">Type</th>
                      <th className="px-3 py-3 font-medium">Details</th>
                      <th className="px-3 py-3 font-medium">Score</th>
                      <th className="px-3 py-3 font-medium">Risk label</th>
                      <th className="px-3 py-3 font-medium">Status</th>
                      <th className="px-3 py-3 font-medium">Date &amp; time</th>
                      <th className="px-5 py-3"><span className="sr-only">Actions</span></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-ink-700/60">
                    {result.items.map((s) => (
                      <tr key={s.id} onClick={() => navigate(`/scans/${s.id}`)} className="cursor-pointer transition hover:bg-ink-850">
                        <td className="px-5 py-3 font-mono text-slate-400">#{s.id}</td>
                        <td className="px-3 py-3 text-slate-200">{scanTypeLabel(s.scan_type)}</td>
                        <td className="max-w-[260px] truncate px-3 py-3 text-slate-400" title={s.input_summary}>{s.input_summary}</td>
                        <td className="px-3 py-3 font-mono text-white">{s.risk_score ?? '—'}</td>
                        <td className="px-3 py-3"><RiskBadge label={s.risk_label} /></td>
                        <td className="px-3 py-3 text-xs text-slate-400">{s.status === 'completed' ? 'Completed' : 'Insufficient evidence'}</td>
                        <td className="whitespace-nowrap px-3 py-3 text-xs text-slate-400">{formatDate(s.created_at)}</td>
                        <td className="px-5 py-3 text-right">
                          <button type="button" onClick={(e) => remove(e, s)} aria-label={`Delete scan ${s.id}`}
                            className="rounded-lg p-1.5 text-slate-500 hover:bg-rose-500/10 hover:text-rose-300">
                            <Trash2 className="size-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="flex items-center justify-between border-t border-ink-700 px-5 py-3 text-sm text-mist">
                <span>{result.total} scan{result.total === 1 ? '' : 's'}</span>
                <div className="flex items-center gap-2">
                  <button type="button" className="btn btn-ghost px-2.5 py-1.5" disabled={page === 0} onClick={() => setPage((p) => p - 1)} aria-label="Previous page">
                    <ChevronLeft className="size-4" />
                  </button>
                  <span className="font-mono text-xs">{page + 1} / {pages}</span>
                  <button type="button" className="btn btn-ghost px-2.5 py-1.5" disabled={page + 1 >= pages} onClick={() => setPage((p) => p + 1)} aria-label="Next page">
                    <ChevronRight className="size-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
