import { Link, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { EmptyState } from './components/ui'
import Dashboard from './pages/Dashboard'
import { AnalyzeMessage, CompanyChecker, ProfileChecker, RecruiterDetector, ScanUrl } from './pages/AnalyzerPages'
import DocumentScanner from './pages/DocumentScanner'
import ScanHistory from './pages/ScanHistory'
import ScanDetail from './pages/ScanDetail'
import Reports from './pages/Reports'
import ReportView from './pages/ReportView'
import Settings from './pages/Settings'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="analyze/message" element={<AnalyzeMessage />} />
        <Route path="analyze/url" element={<ScanUrl />} />
        <Route path="analyze/profile" element={<ProfileChecker />} />
        <Route path="analyze/recruiter" element={<RecruiterDetector />} />
        <Route path="analyze/company" element={<CompanyChecker />} />
        <Route path="analyze/document" element={<DocumentScanner />} />
        <Route path="history" element={<ScanHistory />} />
        <Route path="scans/:id" element={<ScanDetail />} />
        <Route path="reports" element={<Reports />} />
        <Route path="reports/:id" element={<ReportView />} />
        <Route path="settings" element={<Settings />} />
        <Route path="*" element={
          <div className="card"><EmptyState title="Page not found" action={<Link to="/" className="btn btn-primary">Go to dashboard</Link>} /></div>
        } />
      </Route>
    </Routes>
  )
}
