// All communication with the FastAPI backend lives here.
// Every function below maps to exactly one backend route in backend/app/routes.py or main.py.
import axios from 'axios'

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/+$/, '')

const http = axios.create({ baseURL: `${API_BASE_URL}/api/v1`, timeout: 60000 })
const data = (promise) => promise.then((res) => res.data)

export const api = {
  analyzeMessage: (body) => data(http.post('/analyze/message', body)),        // POST /api/v1/analyze/message
  analyzeUrl: (body) => data(http.post('/analyze/url', body)),                // POST /api/v1/analyze/url
  analyzeProfile: (body) => data(http.post('/analyze/profile', body)),        // POST /api/v1/analyze/profile
  analyzeRecruiter: (body) => data(http.post('/analyze/recruiter', body)),    // POST /api/v1/analyze/recruiter
  analyzeCompany: (body) => data(http.post('/analyze/company', body)),        // POST /api/v1/analyze/company
  analyzeDocument: (file, onUploadProgress) => {                              // POST /api/v1/analyze/document
    const form = new FormData()
    form.append('file', file)
    return data(http.post('/analyze/document', form, { onUploadProgress }))
  },
  listScans: (params) => data(http.get('/scans', { params })),                // GET /api/v1/scans
  getScan: (id) => data(http.get(`/scans/${id}`)),                            // GET /api/v1/scans/{id}
  deleteScan: (id) => data(http.delete(`/scans/${id}`)),                      // DELETE /api/v1/scans/{id}
  getStats: () => data(http.get('/dashboard/stats')),                         // GET /api/v1/dashboard/stats
  listReports: () => data(http.get('/reports')),                             // GET /api/v1/reports
  getReport: (id) => data(http.get(`/reports/${id}`)),                        // GET /api/v1/reports/{id}
  createReport: (scanId, reportType = 'detailed') =>                          // POST /api/v1/reports
    data(http.post('/reports', { scan_id: scanId, report_type: reportType })),
  health: () => data(axios.get(`${API_BASE_URL}/health`, { timeout: 8000 })), // GET /health
}

/** Turn any Axios error into a short message a person can act on. */
export function errorMessage(err) {
  if (!err?.response) {
    if (err?.code === 'ECONNABORTED') return 'The request took too long. Please try again.'
    return `Cannot reach the backend at ${API_BASE_URL}. Make sure it is running (uvicorn app.main:app --reload).`
  }
  const { status, data: body } = err.response
  const detail = body?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((d) => {
        const field = Array.isArray(d.loc) ? d.loc.filter((p) => p !== 'body').join(' › ') : ''
        const msg = String(d.msg || '').replace(/^Value error, /, '')
        return field ? `${field}: ${msg}` : msg
      })
      .join(' · ')
  }
  if (status === 503) return 'The database is unavailable. Check that MySQL is running.'
  return `Request failed (HTTP ${status}).`
}
