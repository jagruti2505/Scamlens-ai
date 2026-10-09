// Home page: statistics from MySQL, charts, recent scans and quick actions.
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Activity, ArrowRight, Briefcase, Building2, FileSearch, Link2, MessageSquareWarning, Radar,
  ShieldAlert, Siren, UserSearch,
} from 'lucide-react'
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { EmptyState, ErrorAlert, PageHeader, RiskBadge, Spinner } from '../components/ui'
import { api, errorMessage } from '../services/api'
import { formatDate, riskStyle, scanTypeLabel } from '../utils'

const QUICK = [
  { to: '/analyze/message', label: 'Message', icon: MessageSquareWarning },
  { to: '/analyze/url', label: 'URL', icon: Link2 },
  { to: '/analyze/profile', label: 'Profile', icon: UserSearch },
  { to: '/analyze/recruiter', label: 'Job offer', icon: Briefcase },
  { to: '/analyze/company', label: 'Company', icon: Building2 },
  { to: '/analyze/document', label: 'Document', icon: FileSearch },
]
const CATEGORY_COLORS = ['#3b82f6', '#22d3ee', '#818cf8', '#38bdf8', '#2dd4bf', '#a78bfa']
const SHORT_LABEL = { 'Lower Observed Risk': 'Lower', 'Very High Risk': 'Very High', 'Insufficient Evidence': 'Insufficient' }

function StatCard({ icon: Icon, label, value, accent, delay }) {
  return (
    <div className="card relative overflow-hidden p-5 animate-rise" style={{ animationDelay: `${delay}ms` }}>
      <div className="absolute -right-6 -top-6 size-24 rounded-full blur-2xl" style={{ background: `${accent}22` }} />
      <div className="flex items-center justify-between">
        <span className="text-sm text-mist">{label}</span>
        <Icon className="size-5" style={{ color: accent }} />
      </div>
      <div className="mt-3 font-mono text-4xl font-semibold text-white">{value}</div>
    </div>
  )
}

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const item = payload[0]
  return (
    <div className="rounded-lg border border-ink-600 bg-ink-900 px-3 py-2 text-xs shadow-xl">
      <div className="text-slate-300">{item.payload.full || item.payload.name}</div>
      <div className="font-mono text-base text-white">{item.value}</div>
    </div>
  )
}

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(() => {
    setError('')
    api.getStats().then(setStats).catch((err) => setError(errorMessage(err)))
  }, [])
  useEffect(load, [load])

  const quickActions = (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
      {QUICK.map(({ to, label, icon: Icon }, i) => (
        <Link key={to} to={to} style={{ animationDelay: `${i * 40}ms` }}
          className="group card flex items-center gap-3 p-4 transition hover:-translate-y-0.5 hover:border-cyan-400/40 animate-rise">
          <div className="grid size-9 place-items-center rounded-lg bg-ink-800 ring-1 ring-ink-600 group-hover:ring-cyan-400/40">
            <Icon className="size-4 text-cyan-300" />
          </div>
          <span className="text-sm font-medium text-slate-200">{label}</span>
        </Link>
      ))}
    </div>
  )

  if (error) return (<><PageHeader icon={Radar} title="Dashboard" /><ErrorAlert message={error} onRetry={load} /></>)
  if (!stats) return <Spinner label="Loading dashboard…" />

  const riskData = stats.risk_distribution.map((d) => ({ name: SHORT_LABEL[d.name] || d.name, full: d.name, value: d.count }))
  const categoryData = stats.scan_categories.filter((c) => c.count > 0)
    .map((c) => ({ name: scanTypeLabel(c.name), value: c.count }))

  return (
    <div className="space-y-6">
      <PageHeader icon={Radar} title="Threat overview"
        subtitle="Scan suspicious messages, links, recruiters, companies and documents. Every result explains why it was flagged."
        actions={<Link to="/analyze/message" className="btn btn-primary">New scan <ArrowRight className="size-4" /></Link>} />

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard icon={Activity} label="Total scans" value={stats.total_scans} accent="#22d3ee" delay={0} />
        <StatCard icon={Siren} label="High-risk detections" value={stats.high_risk} accent="#f43f5e" delay={60} />
        <StatCard icon={Link2} label="Suspicious URLs" value={stats.suspicious_urls} accent="#fb923c" delay={120} />
        <StatCard icon={Briefcase} label="Potential job scams" value={stats.potential_job_scams} accent="#facc15" delay={180} />
      </div>

      <section>
        <h2 className="section-title">Start a new scan</h2>
        {quickActions}
      </section>

      {stats.total_scans === 0 ? (
        <div className="card">
          <EmptyState icon={ShieldAlert} title="No scans yet"
            action={<Link to="/analyze/message" className="btn btn-primary">Analyze your first message</Link>}>
            Charts and history appear here after your first scan. Try a suspicious SMS, email or job offer — each page has a "Load example" button.
          </EmptyState>
        </div>
      ) : (
        <>
          <div className="grid gap-5 lg:grid-cols-5">
            <div className="card p-5 lg:col-span-3">
              <h2 className="section-title">Risk distribution</h2>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={riskData} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
                    <CartesianGrid stroke="#15284f" vertical={false} />
                    <XAxis dataKey="name" tick={{ fill: '#8fa3c7', fontSize: 11 }} axisLine={false} tickLine={false} interval={0} />
                    <YAxis allowDecimals={false} tick={{ fill: '#8fa3c7', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(34,211,238,0.06)' }} />
                    <Bar dataKey="value" radius={[6, 6, 0, 0]} maxBarSize={46}>
                      {riskData.map((d) => <Cell key={d.full} fill={riskStyle(d.full).hex} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="card p-5 lg:col-span-2">
              <h2 className="section-title">Scan categories</h2>
              <div className="flex h-64 items-center gap-4">
                <div className="h-full flex-1">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={categoryData} dataKey="value" nameKey="name" innerRadius="58%" outerRadius="88%" paddingAngle={3} stroke="none">
                        {categoryData.map((d, i) => <Cell key={d.name} fill={CATEGORY_COLORS[i % CATEGORY_COLORS.length]} />)}
                      </Pie>
                      <Tooltip content={<ChartTooltip />} />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <ul className="space-y-2 text-sm">
                  {categoryData.map((d, i) => (
                    <li key={d.name} className="flex items-center gap-2 text-slate-300">
                      <span className="size-2.5 rounded-sm" style={{ background: CATEGORY_COLORS[i % CATEGORY_COLORS.length] }} />
                      {d.name}<span className="font-mono text-slate-500">{d.value}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="card overflow-hidden">
            <div className="flex items-center justify-between px-5 pt-5">
              <h2 className="section-title mb-0">Recent scans</h2>
              <Link to="/history" className="text-sm text-cyan-300 hover:text-cyan-200">View all</Link>
            </div>
            <ul className="mt-3 divide-y divide-ink-700/70">
              {stats.recent_scans.map((s) => (
                <li key={s.id}>
                  <Link to={`/scans/${s.id}`} className="flex flex-wrap items-center gap-x-4 gap-y-1 px-5 py-3.5 transition hover:bg-ink-850">
                    <span className="w-12 font-mono text-xs text-slate-500">#{s.id}</span>
                    <span className="w-36 text-sm text-slate-300">{scanTypeLabel(s.scan_type)}</span>
                    <span className="min-w-0 flex-1 truncate text-sm text-slate-400">{s.input_summary}</span>
                    <RiskBadge label={s.risk_label} score={s.risk_score} />
                    <span className="w-40 text-right text-xs text-slate-500">{formatDate(s.created_at)}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  )
}
