// App shell: sidebar navigation (collapsible on mobile) + page content.
import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import {
  Briefcase, Building2, FileSearch, FileText, History, LayoutDashboard, Link2, UserSearch,
  Menu, MessageSquareWarning, Settings, X,
} from 'lucide-react'

export const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/analyze/message', label: 'Analyze Message', icon: MessageSquareWarning },
  { to: '/analyze/url', label: 'Scan URL', icon: Link2 },
  { to: '/analyze/profile', label: 'LinkedIn Profile Checker', icon: UserSearch },
  { to: '/analyze/recruiter', label: 'Recruiter & Job Scam Detector', icon: Briefcase },
  { to: '/analyze/company', label: 'Company Checker', icon: Building2 },
  { to: '/analyze/document', label: 'Document Scanner', icon: FileSearch },
  { to: '/history', label: 'Scan History', icon: History },
  { to: '/reports', label: 'Reports', icon: FileText },
  { to: '/settings', label: 'Settings', icon: Settings },
]

function Logo() {
  return (
    <div className="flex items-center gap-3">
      <div className="relative grid size-10 place-items-center overflow-hidden rounded-xl bg-ink-800 ring-1 ring-cyan-400/30">
        <svg viewBox="0 0 32 32" className="size-6" aria-hidden="true">
          <circle cx="14" cy="14" r="7" fill="none" stroke="#22d3ee" strokeWidth="2.5" />
          <path d="M19 19l6 6" stroke="#22d3ee" strokeWidth="2.5" strokeLinecap="round" />
          <circle cx="14" cy="14" r="2.5" fill="#3b82f6" />
        </svg>
        <span className="absolute inset-x-0 top-0 h-1/2 bg-gradient-to-b from-cyan-300/30 to-transparent animate-scan" />
      </div>
      <div className="leading-tight">
        <div className="font-display text-[15px] font-bold tracking-wide text-white">SCAMLENS <span className="text-cyan-300">AI</span></div>
        <div className="text-[11px] text-mist">See the scam before you click</div>
      </div>
    </div>
  )
}

export default function Layout() {
  const [open, setOpen] = useState(false)

  const nav = (
    <nav className="flex flex-col gap-1">
      {NAV.map(({ to, label, icon: Icon, end }) => (
        <NavLink key={to} to={to} end={end} onClick={() => setOpen(false)}
          className={({ isActive }) =>
            `group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${
              isActive ? 'bg-gradient-to-r from-blue-500/20 to-cyan-400/5 text-white ring-1 ring-cyan-400/20'
                       : 'text-slate-400 hover:bg-ink-800 hover:text-slate-100'}`}>
          {({ isActive }) => (
            <>
              {isActive && <span className="absolute -left-3 top-2 bottom-2 w-1 rounded-r bg-cyan-300" />}
              <Icon className={`size-[18px] shrink-0 ${isActive ? 'text-cyan-300' : 'text-slate-500 group-hover:text-slate-300'}`} />
              <span className="truncate">{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  )

  return (
    <div className="min-h-screen lg:pl-72">
      {/* Desktop sidebar */}
      <aside className="no-print fixed inset-y-0 left-0 hidden w-72 flex-col border-r border-ink-700/70 bg-ink-900/90 px-6 py-6 backdrop-blur lg:flex">
        <Logo />
        <div className="mt-8 flex-1 overflow-y-auto pr-1">{nav}</div>
        <p className="mt-6 text-[11px] leading-relaxed text-slate-500">
          Local, shared scan history · no accounts. Do not deploy publicly with sensitive data.
        </p>
      </aside>

      {/* Mobile top bar */}
      <header className="no-print sticky top-0 z-30 flex items-center justify-between border-b border-ink-700/70 bg-ink-900/90 px-4 py-3 backdrop-blur lg:hidden">
        <Logo />
        <button type="button" onClick={() => setOpen(true)} className="btn btn-ghost px-3" aria-label="Open menu">
          <Menu className="size-5" />
        </button>
      </header>
      {open && (
        <div className="no-print fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setOpen(false)} />
          <div className="absolute inset-y-0 left-0 w-72 overflow-y-auto border-r border-ink-700 bg-ink-900 px-6 py-6 animate-rise">
            <div className="mb-8 flex items-center justify-between">
              <Logo />
              <button type="button" onClick={() => setOpen(false)} aria-label="Close menu" className="text-slate-400 hover:text-white">
                <X className="size-5" />
              </button>
            </div>
            {nav}
          </div>
        </div>
      )}

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-10 lg:py-10">
        <Outlet />
      </main>
    </div>
  )
}
