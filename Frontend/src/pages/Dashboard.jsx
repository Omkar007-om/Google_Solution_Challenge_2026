import DashboardCards from '../components/DashboardCards.jsx'
import TransactionTable from '../components/TransactionTable.jsx'
import RiskGauge from '../components/RiskGauge.jsx'
import ActivityFeed from '../components/ActivityFeed.jsx'
import SARReportPanel from '../components/SARReportPanel.jsx'
import { motion } from 'framer-motion'

export default function Dashboard({ data }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className="flex min-h-0 flex-1 flex-col gap-4"
    >
      <div className="flex items-end justify-between gap-4">
        <div className="min-w-0">
          <div className="text-2xl font-extrabold tracking-tight text-white">Suspicious Activity Report</div>
          <div className="mono mt-1 truncate text-[12px] text-slate-200/65">
            Premium fintech intelligence dashboard • fraud detection + compliance analysis
          </div>
        </div>
        <div className="hidden items-center gap-2 md:flex">
          <div className="mono rounded-xl bg-white/[0.06] px-3 py-2 text-[11px] ring-1 ring-white/10">ENV: PROD-SIM</div>
          <div className="mono rounded-xl bg-white/[0.06] px-3 py-2 text-[11px] ring-1 ring-white/10">REGION: GLOBAL</div>
        </div>
      </div>

      <DashboardCards totals={data.totals} />

      <div className="grid min-h-0 grid-cols-1 gap-4 xl:grid-cols-[1.25fr_0.75fr]">
        <TransactionTable transactions={data.transactions} suspiciousThreshold={data.suspiciousThreshold} />
        <div className="grid min-h-0 grid-cols-1 gap-4">
          <RiskGauge value={data.totals.riskScore} />
          <ActivityFeed items={data.activity} />
        </div>
      </div>

      <div className="min-h-0">
        <SARReportPanel sar={data.sar} />
      </div>
    </motion.div>
  )
}

