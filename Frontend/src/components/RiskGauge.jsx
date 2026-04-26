import { ResponsiveContainer, RadialBar, RadialBarChart } from 'recharts'
import { motion } from 'framer-motion'
import { useMemo } from 'react'

function riskToColor(r) {
  if (r < 35) return 'rgba(52, 211, 153, 0.85)'
  if (r < 70) return 'rgba(251, 191, 36, 0.85)'
  return 'rgba(244, 63, 94, 0.85)'
}

export default function RiskGauge({ value = 0 }) {
  const v = Math.max(0, Math.min(100, value))
  const chartData = useMemo(() => [{ name: 'risk', value: v, fill: riskToColor(v) }], [v])

  return (
    <div className="glass-strong soft-neu relative overflow-hidden rounded-2xl border border-white/[0.12] p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-white/90">Risk Gauge</div>
          <div className="mono mt-0.5 text-[11px] text-slate-200/60">Model + rules blended score</div>
        </div>
        <div className="mono rounded-xl bg-white/[0.06] px-3 py-2 text-[12px] ring-1 ring-white/10">
          {value}/100
        </div>
      </div>

      <div className="mt-2 h-[210px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%"
            cy="56%"
            innerRadius="70%"
            outerRadius="96%"
            barSize={14}
            startAngle={210}
            endAngle={-30}
            data={chartData}
          >
            <RadialBar dataKey="value" cornerRadius={16} background={{ fill: 'rgba(255,255,255,0.10)' }} />
          </RadialBarChart>
        </ResponsiveContainer>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.08 }}
          className="pointer-events-none absolute inset-x-0 bottom-4 text-center"
        >
          <div className="text-xs font-semibold text-white/85">Operational posture</div>
          <div className="mono mt-1 text-[11px] text-slate-200/65">
            {value < 35 ? 'Low volatility • monitor' : value < 70 ? 'Elevated • review evidence' : 'High risk • escalate'}
          </div>
        </motion.div>
      </div>

      <div className="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-nexus-neon/12 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-28 -left-24 h-64 w-64 rounded-full bg-nexus-violet/12 blur-3xl" />
    </div>
  )
}

