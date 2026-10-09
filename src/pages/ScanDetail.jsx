// Full detail view for one stored scan.
import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ListChecks } from 'lucide-react'
import ResultView from '../components/ResultView'
import { EmptyState, ErrorAlert, PageHeader, Spinner } from '../components/ui'
import { api, errorMessage } from '../services/api'

export default function ScanDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [scan, setScan] = useState(null)
  const [error, setError] = useState('')
  const [missing, setMissing] = useState(false)

  const load = useCallback(() => {
    setError(''); setMissing(false); setScan(null)
    api.getScan(id).then(setScan).catch((err) => {
      if (err.response?.status === 404) setMissing(true)
      else setError(errorMessage(err))
    })
  }, [id])
  useEffect(load, [load])

  return (
    <div>
      <PageHeader icon={ListChecks} title={`Scan #${id}`} subtitle="Detailed findings, evidence and recommendations."
        actions={<Link to="/history" className="btn btn-ghost">Back to history</Link>} />
      <ErrorAlert message={error} onRetry={load} />
      {missing && (
        <div className="card"><EmptyState title="Scan not found" action={<Link to="/history" className="btn btn-primary">Open scan history</Link>}>
          It may have been deleted.
        </EmptyState></div>
      )}
      {!scan && !error && !missing && <Spinner />}
      {scan && <ResultView scan={scan} onDeleted={() => navigate('/history')} />}
    </div>
  )
}
