// Upload a PDF, DOCX, TXT or image and scan the extracted text.
import { useRef, useState } from 'react'
import { FileSearch, FileUp, Loader2, ScanSearch, X } from 'lucide-react'
import { ErrorAlert, PageHeader } from '../components/ui'
import ResultView from '../components/ResultView'
import { api, errorMessage } from '../services/api'

const ACCEPT = ['.pdf', '.docx', '.txt', '.png', '.jpg', '.jpeg', '.webp']
const MAX_MB = 5

export default function DocumentScanner() {
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [scan, setScan] = useState(null)
  const inputRef = useRef(null)
  const resultRef = useRef(null)

  function choose(selected) {
    setError(''); setScan(null)
    if (!selected) return
    const ext = selected.name.slice(selected.name.lastIndexOf('.')).toLowerCase()
    if (!ACCEPT.includes(ext)) { setError('Unsupported file type. Use PDF, DOCX, TXT, PNG, JPG or WEBP.'); return }
    if (selected.size > MAX_MB * 1024 * 1024) { setError(`File is larger than ${MAX_MB} MB.`); return }
    setFile(selected)
  }

  async function analyze() {
    if (!file) { setError('Choose a file first.'); return }
    setLoading(true); setError(''); setProgress(0)
    try {
      const result = await api.analyzeDocument(file, (e) => e.total && setProgress(Math.round((e.loaded / e.total) * 100)))
      setScan(result)
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader icon={FileSearch} title="Document Scanner"
        subtitle="Upload an offer letter, invoice or notice. Text is extracted in memory and checked for fake job offers, payment instructions, phishing links and requests for personal data. The file itself is not saved." />
      <div className="card space-y-4 p-5 sm:p-6 animate-rise">
        <div
          role="button" tabIndex={0}
          onClick={() => inputRef.current?.click()}
          onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && inputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => { e.preventDefault(); setDragging(false); choose(e.dataTransfer.files?.[0]) }}
          className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-12 text-center transition ${
            dragging ? 'border-cyan-300 bg-cyan-400/5' : 'border-ink-600 hover:border-ink-500 hover:bg-ink-850/60'}`}>
          <div className="mb-3 grid size-14 place-items-center rounded-2xl bg-ink-800 ring-1 ring-ink-600">
            <FileUp className="size-6 text-cyan-300" />
          </div>
          <p className="font-medium text-slate-100">Drop a file here or click to browse</p>
          <p className="mt-1 text-sm text-mist">PDF, DOCX, TXT, PNG, JPG or WEBP · up to {MAX_MB} MB</p>
          <input ref={inputRef} type="file" accept={ACCEPT.join(',')} className="hidden"
            onChange={(e) => { choose(e.target.files?.[0]); e.target.value = '' }} />
        </div>

        {file && (
          <div className="flex items-center gap-3 rounded-xl border border-ink-700 bg-ink-850 px-4 py-3">
            <FileSearch className="size-5 text-cyan-300" />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-slate-100">{file.name}</p>
              <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
              {loading && (
                <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-ink-700">
                  <div className="h-full rounded-full bg-gradient-to-r from-blue-500 to-cyan-300 transition-all" style={{ width: `${progress || 8}%` }} />
                </div>
              )}
            </div>
            {!loading && (
              <button type="button" onClick={() => { setFile(null); setScan(null) }} aria-label="Remove file" className="text-slate-500 hover:text-white">
                <X className="size-4" />
              </button>
            )}
          </div>
        )}

        <ErrorAlert message={error} />
        <div className="flex flex-wrap items-center gap-3">
          <button type="button" onClick={analyze} disabled={!file || loading} className="btn btn-primary">
            {loading ? <Loader2 className="size-4 animate-spin" /> : <ScanSearch className="size-4" />}
            {loading ? (progress < 100 ? 'Uploading…' : 'Analyzing…') : 'Analyze document'}
          </button>
          <p className="text-xs text-slate-500">Image text recognition requires Tesseract OCR on the server; otherwise the scan reports it as unavailable.</p>
        </div>
      </div>
      <div ref={resultRef} className="scroll-mt-6 pt-6">{scan && <ResultView scan={scan} compact />}</div>
    </div>
  )
}
