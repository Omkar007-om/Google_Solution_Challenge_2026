import { motion } from 'framer-motion'
import { AlertTriangle, BarChart3, FileText, LayoutDashboard, ListChecks, Radar } from 'lucide-react'
import clsx from 'clsx'

const NAV = [
  { id: 'dashboard', label: 'Dashboard', Icon: LayoutDashboard },
  { id: 'transactions', label: 'Transactions', Icon: ListChecks },
  { id: 'risk', label: 'Risk Analysis', Icon: Radar },
  { id: 'reports', label: 'Reports', Icon: FileText },
  { id: 'alerts', label: 'Alerts', Icon: AlertTriangle },
]

export default function Sidebar({ active, onChange }) {
  return (
    <aside className="hidden h-full w-[260px] flex-col md:flex">
      <div className="glass-strong glow-ring soft-neu relative flex h-full flex-col overflow-hidden rounded-2xl p-4">
        <div className="absolute -left-16 -top-16 h-40 w-40 rounded-full bg-nexus-neon/[0.15] blur-2xl" />
        <div className="absolute -bottom-24 -right-24 h-56 w-56 rounded-full bg-nexus-violet/[0.15] blur-2xl" />

        <div className="relative flex items-center gap-3 px-1 py-2">
          <div className="grid h-11 w-11 place-items-center rounded-xl bg-white/[0.06] ring-1 ring-white/10">
            <BarChart3 className="h-5 w-5 text-nexus-cyan" />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold tracking-wide text-white">NEXUS</div>
            <div className="mono truncate text-[11px] text-slate-200/70">SAR Intelligence</div>
          </div>
        </div>

        <div className="mt-4 space-y-2">
          {NAV.map(({ id, label, Icon }) => {
            const isActive = active === id
            return (
              <motion.button
                key={id}
                type="button"
                onClick={() => onChange?.(id)}
                whileHover={{ scale: 1.02, x: 4 }}
                whileTap={{ scale: 0.99 }}
                className={clsx(
                  'group relative flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left transition',
                  'border border-white/10 bg-white/5 hover:bg-white/8',
                  isActive &&
                    'bg-white/10 border-white/[0.15] shadow-[0_0_0_1px_rgba(79,209,255,0.18),0_18px_60px_rgba(0,0,0,0.45)]',
                )}
              >
                <div
                  className={clsx(
                    'grid h-9 w-9 place-items-center rounded-lg ring-1 ring-white/10 transition',
                    isActive ? 'bg-nexus-neon/10 ring-nexus-neon/30' : 'bg-white/5 group-hover:bg-white/8',
                  )}
                >
                  <Icon className={clsx('h-4.5 w-4.5', isActive ? 'text-nexus-cyan' : 'text-slate-200/85')} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className={clsx('text-[13px] font-medium', isActive ? 'text-white' : 'text-slate-100/85')}>
                    {label}
                  </div>
                  <div className="mono truncate text-[11px] text-slate-200/55">
                    {id === 'dashboard'
                      ? 'Overview'
                      : id === 'transactions'
                        ? 'Live ledger'
                        : id === 'risk'
                          ? 'Model evidence'
                          : id === 'reports'
                            ? 'SAR drafts'
                            : 'Threat signals'}
                  </div>
                </div>

                <div
                  className={clsx(
                    'absolute inset-0 -z-10 opacity-0 transition-opacity',
                    'bg-[radial-gradient(600px_200px_at_20%_50%,rgba(79,209,255,0.16),transparent_60%)]',
                    isActive ? 'opacity-100' : 'group-hover:opacity-60',
                  )}
                />
              </motion.button>
            )
          })}
        </div>

        <div className="mt-auto pt-4">
          <div className="glass rounded-xl p-3">
            <div className="flex items-center justify-between">
              <div className="text-xs font-semibold text-white/90">System</div>
              <div className="mono text-[10px] text-emerald-300/90">LIVE</div>
            </div>
            <div className="mt-2 h-2 overflow-hidden rounded-full bg-white/[0.06] ring-1 ring-white/10">
              <div className="h-full w-[76%] bg-gradient-to-r from-nexus-neon/70 via-nexus-cyan/70 to-nexus-violet/70" />
            </div>
            <div className="mt-2 flex items-center justify-between text-[11px] text-slate-200/70">
              <span className="mono">Latency</span>
              <span className="mono">18ms</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}

