// Generic "fill in a form → send to backend → show result" page used by the text-based scanners.
import { useRef, useState } from 'react'
import { Eraser, Loader2, ScanSearch } from 'lucide-react'
import { ErrorAlert, Field, PageHeader } from './ui'
import ResultView from './ResultView'
import { errorMessage } from '../services/api'

/**
 * fields: [{ name, label, type: 'text'|'textarea'|'email'|'url', placeholder, optional, hint, rows, span }]
 * submit: async (values) => scan
 * validate: (values) => error string or ''
 */
export default function AnalyzerForm({ icon, title, subtitle, fields, submit, validate, example, tips }) {
  const empty = Object.fromEntries(fields.map((f) => [f.name, '']))
  const [values, setValues] = useState(empty)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [scan, setScan] = useState(null)
  const resultRef = useRef(null)

  const update = (name) => (e) => setValues((v) => ({ ...v, [name]: e.target.value }))

  async function onSubmit(e) {
    e.preventDefault()
    const problem = validate?.(values)
    if (problem) { setError(problem); return }
    setLoading(true); setError(''); setScan(null)
    try {
      // Send only filled-in fields; empty strings become "not provided".
      const body = Object.fromEntries(Object.entries(values).filter(([, v]) => v.trim() !== ''))
      const result = await submit(body)
      setScan(result)
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader icon={icon} title={title} subtitle={subtitle} />
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]">
        <form onSubmit={onSubmit} className="card space-y-4 p-5 sm:p-6 animate-rise">
          <div className="grid gap-4 sm:grid-cols-2">
            {fields.map((f) => (
              <div key={f.name} className={f.span === 1 ? '' : 'sm:col-span-2'}>
                <Field label={f.label} optional={f.optional} hint={f.hint}>
                  {f.type === 'textarea' ? (
                    <textarea className="input resize-y leading-relaxed" rows={f.rows || 6} placeholder={f.placeholder}
                      value={values[f.name]} onChange={update(f.name)} maxLength={f.maxLength || 20000} />
                  ) : (
                    <input className="input" type={f.type === 'email' ? 'text' : 'text'} inputMode={f.type === 'url' ? 'url' : undefined}
                      placeholder={f.placeholder} value={values[f.name]} onChange={update(f.name)} maxLength={f.maxLength || 2048}
                      autoComplete="off" spellCheck={false} />
                  )}
                </Field>
              </div>
            ))}
          </div>
          <ErrorAlert message={error} />
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <button type="submit" disabled={loading} className="btn btn-primary">
              {loading ? <Loader2 className="size-4 animate-spin" /> : <ScanSearch className="size-4" />}
              {loading ? 'Analyzing…' : 'Analyze'}
            </button>
            {example && (
              <button type="button" className="btn btn-ghost" onClick={() => { setValues({ ...empty, ...example }); setError('') }}>
                Load example
              </button>
            )}
            <button type="button" className="btn btn-ghost" onClick={() => { setValues(empty); setScan(null); setError('') }}>
              <Eraser className="size-4" />Clear
            </button>
          </div>
          <p className="text-xs text-slate-500">
            Only a short description of your input and the detected warning signs (with personal details masked) are saved — not the full text.
          </p>
        </form>
        {tips && (
          <aside className="card h-fit p-5 animate-rise">
            <h3 className="section-title">What we look for</h3>
            <ul className="space-y-2 text-sm text-slate-300">
              {tips.map((t) => <li key={t} className="flex gap-2"><span className="mt-2 size-1 shrink-0 rounded-full bg-cyan-300" />{t}</li>)}
            </ul>
          </aside>
        )}
      </div>
      <div ref={resultRef} className="scroll-mt-6 pt-6">
        {scan && <ResultView scan={scan} compact />}
      </div>
    </div>
  )
}
