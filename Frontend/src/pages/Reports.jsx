import { useMemo, useState } from 'react'
import { motion } from 'framer-motion'
import { analyzeCsv } from '../lib/api.js'
import { FileUp, Loader2, Sparkles } from 'lucide-react'

function JsonBlock({ value }) {
  const text = useMemo(() => JSON.stringify(value ?? null, null, 2), [value])
  return (
    <pre className="whitespace-pre-wrap rounded-xl bg-black/25 p-4 font-mono text-[12px] leading-relaxed text-slate-100/85 ring-1 ring-white/10">
      {text}
    </pre>
  )
}

export default function Reports() {
  const [subject, setSubject] = useState('ACC-0042')
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function onAnalyze() {
    if (!file) return
    setBusy(true)
    setError('')
    try {
      const res = await analyzeCsv({ file, subjectAccount: subject })
      setResult(res)
    } catch (e) {
      setError(e?.message || 'Analysis failed')
      setResult(null)
    } finally {
      setBusy(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className="flex min-h-0 flex-1 flex-col gap-4"
    >
      <div className="flex items-end justify-between gap-4">
        <div className="min-w-0">
          <div className="text-2xl font-extrabold tracking-tight text-white">Reports • Dataset Analyzer</div>
          <div className="mono mt-1 truncate text-[12px] text-slate-200/65">
            Upload a transaction dataset and generate a SAR report via the backend pipeline
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <div className="glass-strong soft-neu rounded-2xl border border-white/[0.12] p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-white/90">Upload Dataset</div>
              <div className="mono mt-0.5 text-[11px] text-slate-200/60">CSV only • header required</div>
            </div>
            <div className="grid h-10 w-10 place-items-center rounded-2xl bg-nexus-violet/[0.12] ring-1 ring-nexus-violet/20">
              <Sparkles className="h-4 w-4 text-violet-200" />
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <div>
              <div className="mono mb-1 text-[11px] text-slate-200/70">Subject account (optional)</div>
              <input
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full rounded-xl bg-white/[0.06] px-3 py-2 text-[12px] text-slate-100 outline-none ring-1 ring-white/10 focus:ring-2 focus:ring-nexus-neon/40"
                placeholder="ACC-0042"
              />
            </div>

            <label className="block">
              <div className="mono mb-1 text-[11px] text-slate-200/70">CSV file</div>
              <div className="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-4 hover:bg-white/[0.07]">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-white/85">{file ? file.name : 'Choose file…'}</div>
                  <div className="mono mt-1 truncate text-[11px] text-slate-200/55">
                    {file ? `${Math.round(file.size / 1024)} KB` : 'Expected columns: amount, location, time, risk_score (best-effort)'}
                  </div>
                </div>
                <div className="grid h-11 w-11 place-items-center rounded-2xl bg-white/[0.06] ring-1 ring-white/10">
                  <FileUp className="h-5 w-5 text-nexus-cyan" />
                </div>
              </div>
              <input
                type="file"
                accept=".csv,text/csv"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
              />
            </label>

            <button
              type="button"
              disabled={!file || busy}
              onClick={onAnalyze}
              className="group relative inline-flex w-full items-center justify-center gap-3 overflow-hidden rounded-2xl bg-white/10 px-4 py-3 text-sm font-semibold text-white ring-1 ring-white/[0.15] hover:bg-white/[0.14] disabled:cursor-not-allowed disabled:opacity-50"
            >
              {busy ? <Loader2 className="h-4.5 w-4.5 animate-spin" /> : <Sparkles className="h-4.5 w-4.5" />}
              <span>Analyze & Generate SAR</span>
              <span className="pointer-events-none absolute inset-0 opacity-70">
                <span className="absolute -left-1/3 top-0 h-full w-1/2 bg-gradient-to-r from-transparent via-white/20 to-transparent transition-transform group-hover:translate-x-[180%]" />
              </span>
            </button>

            {error ? (
              <div className="rounded-xl bg-rose-500/[0.10] p-3 text-[12px] text-rose-100 ring-1 ring-rose-300/20">
                {error}
              </div>
            ) : null}
          </div>
        </div>

        <div className="glass-strong soft-neu min-h-0 rounded-2xl border border-white/[0.12] p-4">
          <div className="text-sm font-semibold text-white/90">Analysis Output</div>
          <div className="mono mt-0.5 text-[11px] text-slate-200/60">Pipeline result + trace</div>

          <div className="mt-4 grid min-h-0 grid-cols-1 gap-4">
            <div>
              <div className="mono mb-2 text-[11px] text-slate-200/65">Result</div>
              <JsonBlock value={result?.result} />
            </div>
            <div>
              <div className="mono mb-2 text-[11px] text-slate-200/65">Trace</div>
              <JsonBlock value={result?.metadata} />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

