// Read-only system status and information. Secrets are configured in backend/.env, never here.
import { useCallback, useEffect, useState } from 'react'
import { CheckCircle2, CircleSlash, Database, RefreshCw, Settings as SettingsIcon, ShieldCheck } from 'lucide-react'
import { ErrorAlert, PageHeader, RiskBadge } from '../components/ui'
import { API_BASE_URL, api, errorMessage } from '../services/api'

function Row({ label, on, detail }) {
  return (
    <div className="flex items-center justify-between gap-4 py-3">
      <div>
        <p className="text-sm text-slate-200">{label}</p>
        {detail && <p className="text-xs text-slate-500">{detail}</p>}
      </div>
      {on ? (
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-emerald-300"><CheckCircle2 className="size-4" />Enabled</span>
      ) : (
        <span className="inline-flex items-center gap-1.5 text-xs font-medium text-slate-500"><CircleSlash className="size-4" />Off</span>
      )}
    </div>
  )
}

const BANDS = [['0–19', 'Lower Observed Risk'], ['20–39', 'Caution'], ['40–59', 'Suspicious'], ['60–79', 'High Risk'], ['80–100', 'Very High Risk']]

export default function Settings() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')
  const [checking, setChecking] = useState(false)

  const check = useCallback(() => {
    setChecking(true); setError('')
    api.health().then(setHealth).catch((err) => { setHealth(null); setError(errorMessage(err)) }).finally(() => setChecking(false))
  }, [])
  useEffect(check, [check])

  const f = health?.features || {}
  return (
    <div className="space-y-5">
      <PageHeader icon={SettingsIcon} title="Settings & Status"
        subtitle="Optional features are switched on in backend/.env. API keys are never sent to or stored in the browser."
        actions={<button type="button" onClick={check} className="btn btn-ghost"><RefreshCw className={`size-4 ${checking ? 'animate-spin' : ''}`} />Check again</button>} />
      <ErrorAlert message={error} />

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-5">
          <h2 className="section-title flex items-center gap-2"><Database className="size-4 text-cyan-300" />Connection</h2>
          <div className="divide-y divide-ink-700/70">
            <div className="flex justify-between py-3 text-sm"><span className="text-mist">Backend URL</span><span className="font-mono text-slate-200">{API_BASE_URL}</span></div>
            <div className="flex justify-between py-3 text-sm"><span className="text-mist">Backend</span>
              <span className={health ? 'text-emerald-300' : 'text-rose-300'}>{health ? 'Reachable' : checking ? 'Checking…' : 'Not reachable'}</span></div>
            <div className="flex justify-between py-3 text-sm"><span className="text-mist">MySQL database</span>
              <span className={health?.database === 'connected' ? 'text-emerald-300' : 'text-rose-300'}>{health ? health.database : '—'}</span></div>
          </div>
        </div>
        <div className="card p-5">
          <h2 className="section-title flex items-center gap-2"><ShieldCheck className="size-4 text-cyan-300" />Optional checks</h2>
          <div className="divide-y divide-ink-700/70">
            <Row label="AI-written summaries" on={f.ai_summary} detail={f.ai_summary ? `Model: ${f.ai_model} · wording only, never adds findings` : 'Set ANTHROPIC_API_KEY'} />
            <Row label="Google Safe Browsing" on={f.safe_browsing} detail="Set GOOGLE_SAFE_BROWSING_API_KEY" />
            <Row label="Live link redirect check" on={f.live_url_fetch} detail="ENABLE_URL_FETCH=true · blocks private/internal addresses" />
            <div className="flex justify-between py-3 text-sm"><span className="text-mist">Maximum upload size</span><span className="font-mono text-slate-200">{f.max_upload_mb ?? '—'} MB</span></div>
          </div>
        </div>
        <div className="card p-5">
          <h2 className="section-title">Risk scale</h2>
          <ul className="space-y-2.5">
            {BANDS.map(([range, label]) => (
              <li key={label} className="flex items-center justify-between text-sm"><span className="font-mono text-slate-400">{range}</span><RiskBadge label={label} /></li>
            ))}
            <li className="flex items-center justify-between text-sm"><span className="text-slate-400">Too little information</span><RiskBadge label="Insufficient Evidence" /></li>
          </ul>
          <p className="mt-4 text-xs leading-relaxed text-slate-500">
            Score = 100 × (1 − Π(1 − weight/100)) over distinct warning signs. It is an estimate, not a probability of fraud, and a low score does not guarantee safety.
          </p>
        </div>
        <div className="card p-5">
          <h2 className="section-title">Privacy & data</h2>
          <ul className="space-y-2 text-sm text-slate-300">
            <li>• There are no user accounts: scan history is one shared, local dataset.</li>
            <li>• Full messages and uploaded files are not stored — only a short description and the findings, with emails and long numbers masked.</li>
            <li>• Uploaded documents are processed in memory and discarded.</li>
            <li>• Do not deploy this app publicly without adding access control, or others could read the shared history.</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
