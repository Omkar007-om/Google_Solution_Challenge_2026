import { motion } from 'framer-motion'
import { useEffect, useMemo, useRef, useState } from 'react'
import { Bot, CheckCircle2, Sparkles } from 'lucide-react'

function Typewriter({ text, start = true, speed = 12 }) {
  const [out, setOut] = useState('')
  const iRef = useRef(0)

  useEffect(() => {
    if (!start) return
    iRef.current = 0

    const id = window.setInterval(() => {
      iRef.current += 1
      setOut(text.slice(0, iRef.current))
      if (iRef.current >= text.length) window.clearInterval(id)
    }, speed)

    return () => window.clearInterval(id)
  }, [start, speed, text])

  return (
    <pre className="whitespace-pre-wrap font-mono text-[12px] leading-relaxed text-slate-100/85">
      {out}
      <span className="inline-block w-2 animate-pulse">▋</span>
    </pre>
  )
}

export default function SARReportPanel({ sar }) {
  const combined = useMemo(() => {
    const lines = [
      `SUMMARY: ${sar?.summary ?? ''}`,
      '',
      'KEY FINDINGS:',
      ...(sar?.keyFindings ?? []).map((k) => `- ${k}`),
      '',
      `RISK EXPLANATION: ${sar?.riskExplanation ?? ''}`,
    ]
    return lines.join('\n')
  }, [sar])

  return (
    <div className="glass-strong soft-neu relative overflow-hidden rounded-2xl border border-white/[0.12]">
      <div className="flex items-center justify-between gap-3 px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded-2xl bg-white/[0.06] ring-1 ring-white/10">
            <Bot className="h-5 w-5 text-nexus-cyan" />
          </div>
          <div className="min-w-0">
            <div className="text-sm font-semibold text-white/90">SAR Report Panel</div>
            <div className="mono mt-0.5 truncate text-[11px] text-slate-200/60">AI generated draft</div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="mono rounded-xl bg-white/[0.06] px-3 py-2 text-[11px] ring-1 ring-white/10">DRAFT</div>
          <motion.div
            animate={{ rotate: [0, 8, -8, 0] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            className="grid h-9 w-9 place-items-center rounded-xl bg-nexus-violet/12 ring-1 ring-nexus-violet/20"
          >
            <Sparkles className="h-4 w-4 text-violet-200" />
          </motion.div>
        </div>
      </div>

      <div className="border-t border-white/10 p-4">
        <div className="rounded-xl bg-black/25 p-4 ring-1 ring-white/10">
          <Typewriter key={combined} text={combined} start={true} speed={10} />
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 rounded-xl bg-emerald-500/10 px-3 py-2 ring-1 ring-emerald-300/20">
            <CheckCircle2 className="h-4 w-4 text-emerald-200" />
            <span className="mono text-[11px] text-emerald-100/90">Evidence linked</span>
          </div>
          <div className="mono rounded-xl bg-white/[0.06] px-3 py-2 text-[11px] ring-1 ring-white/10">Export soon</div>
          <div className="mono rounded-xl bg-white/[0.06] px-3 py-2 text-[11px] ring-1 ring-white/10">Audit ready</div>
        </div>
      </div>

      <div className="pointer-events-none absolute -left-20 -top-20 h-56 w-56 rounded-full bg-nexus-neon/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-24 -right-24 h-64 w-64 rounded-full bg-nexus-violet/10 blur-3xl" />
    </div>
  )
}

