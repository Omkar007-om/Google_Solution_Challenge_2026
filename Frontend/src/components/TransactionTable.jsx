import { motion } from 'framer-motion'
import clsx from 'clsx'
import { useMemo, useState } from 'react'
import { Search } from 'lucide-react'

export default function TransactionTable({ transactions, suspiciousThreshold = 72 }) {
  const [q, setQ] = useState('')

  const filtered = useMemo(() => {
    const s = q.trim().toLowerCase()
    if (!s) return transactions
    return transactions.filter((t) => {
      return (
        t.id.toLowerCase().includes(s) ||
        t.location.toLowerCase().includes(s) ||
        t.merchant.toLowerCase().includes(s) ||
        String(t.risk).includes(s)
      )
    })
  }, [q, transactions])

  return (
    <div className="glass-strong soft-neu relative overflow-hidden rounded-2xl border border-white/[0.12]">
      <div className="flex items-center justify-between gap-3 px-4 py-3">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-white/90">Transactions</div>
          <div className="mono mt-0.5 truncate text-[11px] text-slate-200/60">
            Highlighted when risk ≥ {suspiciousThreshold}
          </div>
        </div>
        <div className="relative w-[260px] max-w-full">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-200/55" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search id / location / merchant…"
            className={clsx(
              'w-full rounded-xl bg-white/[0.06] px-10 py-2 text-[12px] text-slate-100 outline-none',
              'ring-1 ring-white/10 focus:ring-2 focus:ring-nexus-neon/40',
            )}
          />
        </div>
      </div>

      <div className="h-[320px] overflow-auto border-t border-white/10">
        <div className="min-w-[760px]">
          <div className="grid grid-cols-[170px_140px_180px_170px_110px] gap-0 px-4 py-3 text-[11px] uppercase tracking-wider text-slate-200/55">
            <div>ID</div>
            <div>Amount</div>
            <div>Location</div>
            <div>Time</div>
            <div>Risk</div>
          </div>

          <div className="space-y-2 px-3 pb-4">
            {filtered.map((t) => {
              const hot = t.risk >= suspiciousThreshold || t.flagged
              return (
                <motion.div
                  key={t.id}
                  className="perspective-1000"
                  whileHover={{ rotateX: 3, rotateY: -5, y: -2 }}
                  transition={{ type: 'spring', stiffness: 260, damping: 18 }}
                >
                  <div
                    className={clsx(
                      'preserve-3d grid grid-cols-[170px_140px_180px_170px_110px] items-center rounded-xl px-3 py-3',
                      'border ring-1 transition',
                      hot
                        ? 'border-rose-400/25 bg-rose-500/10 ring-rose-400/20'
                        : 'border-white/10 bg-white/5 ring-white/10 hover:bg-white/[0.07]',
                    )}
                  >
                    <div className="mono text-[12px] text-white/90">{t.id}</div>
                    <div className="mono text-[12px] text-slate-100/85">{t.amountLabel}</div>
                    <div className="text-[12px] text-slate-100/85">
                      <div className="font-medium">{t.location}</div>
                      <div className="mono mt-0.5 text-[10px] text-slate-200/55">{t.merchant}</div>
                    </div>
                    <div className="mono text-[11px] text-slate-200/70">{t.time}</div>
                    <div className="flex items-center justify-end gap-2">
                      <div
                        className={clsx(
                          'mono rounded-lg px-2 py-1 text-[11px] ring-1',
                          hot
                            ? 'bg-rose-500/12 text-rose-200 ring-rose-400/25'
                            : 'bg-white/[0.06] text-slate-100/80 ring-white/10',
                        )}
                      >
                        {t.risk}
                      </div>
                      <div className="h-2 w-14 overflow-hidden rounded-full bg-white/[0.06] ring-1 ring-white/10">
                        <div
                          className={clsx(
                            'h-full',
                            hot
                              ? 'bg-gradient-to-r from-orange-400/70 via-rose-400/70 to-rose-500/70'
                              : 'bg-gradient-to-r from-emerald-300/55 via-nexus-neon/55 to-nexus-violet/45',
                          )}
                          style={{ width: `${Math.min(100, Math.max(2, t.risk))}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

