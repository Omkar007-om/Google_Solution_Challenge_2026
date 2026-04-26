import { AnimatePresence, motion } from 'framer-motion'
import clsx from 'clsx'
import { Cpu, ShieldAlert, Siren, Waves } from 'lucide-react'
import { useMemo } from 'react'

function iconFor(kind) {
  if (kind === 'alert') return Siren
  if (kind === 'system') return ShieldAlert
  if (kind === 'model') return Cpu
  return Waves
}

function toneFor(kind) {
  if (kind === 'alert') return 'text-rose-200 bg-rose-500/[0.12] ring-rose-400/20'
  if (kind === 'system') return 'text-nexus-cyan bg-nexus-neon/10 ring-nexus-neon/25'
  if (kind === 'model') return 'text-violet-200 bg-nexus-violet/[0.12] ring-nexus-violet/20'
  return 'text-slate-200 bg-white/[0.06] ring-white/10'
}

export default function ActivityFeed({ items }) {
  const list = useMemo(() => items ?? [], [items])

  return (
    <div className="glass-strong soft-neu relative overflow-hidden rounded-2xl border border-white/[0.12]">
      <div className="flex items-center justify-between gap-3 px-4 py-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-white/90">Activity Feed</div>
          <div className="mono mt-0.5 truncate text-[11px] text-slate-200/60">Real-time style events</div>
        </div>
        <div className="mono rounded-xl bg-white/[0.06] px-3 py-2 text-[11px] ring-1 ring-white/10">LIVE</div>
      </div>

      <div className="h-[320px] overflow-auto border-t border-white/10 px-3 py-3">
        <AnimatePresence initial={false}>
          {list.map((it) => {
            const Icon = iconFor(it.kind)
            return (
              <motion.div
                key={it.t + it.msg}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.28 }}
                className="mb-2 last:mb-0"
              >
                <div className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/5 p-3 hover:bg-white/[0.07]">
                  <div className={clsx('mt-0.5 grid h-9 w-9 place-items-center rounded-xl ring-1', toneFor(it.kind))}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-[12px] font-medium text-slate-100/85">{it.msg}</div>
                    <div className="mono mt-1 text-[10px] text-slate-200/55">{it.t}</div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
      <div className="pointer-events-none absolute -right-24 -top-24 h-56 w-56 rounded-full bg-nexus-neon/10 blur-3xl" />
    </div>
  )
}

