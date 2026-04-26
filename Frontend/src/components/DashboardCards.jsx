import { motion, useMotionTemplate, useMotionValue } from 'framer-motion'
import { ShieldAlert, Sparkles, TrendingUp } from 'lucide-react'
import { useMemo } from 'react'

function TiltCard({ title, value, subtitle, Icon, gradient }) {
  const mx = useMotionValue(0)
  const my = useMotionValue(0)

  const bg = useMotionTemplate`radial-gradient(600px 220px at ${mx}% ${my}%, rgba(79,209,255,0.16), transparent 55%)`

  return (
    <motion.div
      className="perspective-1000"
      onMouseMove={(e) => {
        const r = e.currentTarget.getBoundingClientRect()
        const x = ((e.clientX - r.left) / r.width) * 100
        const y = ((e.clientY - r.top) / r.height) * 100
        mx.set(x)
        my.set(y)
      }}
    >
      <motion.div
        whileHover={{ y: -6, rotateX: 6, rotateY: -8, transition: { duration: 0.25 } }}
        whileTap={{ scale: 0.995 }}
        className="glass-strong soft-neu preserve-3d relative overflow-hidden rounded-2xl border border-white/[0.12] p-5"
      >
        <motion.div className="pointer-events-none absolute inset-0 opacity-80" style={{ background: bg }} />

        <div className="relative flex items-start justify-between gap-3">
          <div className="min-w-0">
            <div className="text-sm font-semibold text-white/90">{title}</div>
            <div className="mt-2 flex items-end gap-3">
              <div className="text-3xl font-extrabold tracking-tight text-white">{value}</div>
              <div className="mono mb-1 text-[11px] text-slate-200/60">{subtitle}</div>
            </div>
          </div>
          <div className="relative">
            <div className={`grid h-12 w-12 place-items-center rounded-2xl ${gradient} ring-1 ring-white/10`}>
              <Icon className="h-5 w-5 text-white" />
            </div>
            <div className="pointer-events-none absolute -inset-2 rounded-3xl blur-xl opacity-40" />
          </div>
        </div>

        <div className="relative mt-5 h-2 overflow-hidden rounded-full bg-white/[0.06] ring-1 ring-white/10">
          <motion.div
            initial={{ x: '-120%' }}
            animate={{ x: '220%' }}
            transition={{ duration: 2.2, repeat: Infinity, ease: 'easeInOut' }}
            className="absolute left-0 top-0 h-full w-1/2 bg-gradient-to-r from-transparent via-white/20 to-transparent"
          />
          <div className="absolute inset-0 opacity-60" />
        </div>
      </motion.div>
    </motion.div>
  )
}

export default function DashboardCards({ totals }) {
  const cards = useMemo(
    () => [
      {
        title: 'Total Transactions',
        value: String(totals.totalTransactions ?? 0),
        subtitle: 'last 24h',
        Icon: TrendingUp,
        gradient: 'bg-gradient-to-br from-nexus-neon/55 via-nexus-cyan/40 to-white/5',
      },
      {
        title: 'Suspicious Transactions',
        value: String(totals.suspiciousTransactions ?? 0),
        subtitle: 'flagged',
        Icon: ShieldAlert,
        gradient: 'bg-gradient-to-br from-rose-500/55 via-orange-400/25 to-white/5',
      },
      {
        title: 'Risk Score',
        value: `${totals.riskScore ?? 0}`,
        subtitle: '/100',
        Icon: Sparkles,
        gradient: 'bg-gradient-to-br from-nexus-violet/55 via-nexus-neon/20 to-white/5',
      },
    ],
    [totals],
  )

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      {cards.map((c) => (
        <TiltCard key={c.title} {...c} />
      ))}
    </div>
  )
}

