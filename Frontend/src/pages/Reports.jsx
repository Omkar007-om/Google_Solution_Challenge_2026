import { useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { analyzeCsv } from '../lib/api.js'
import { FileUp, Loader2, Sparkles, FileText, Activity, ShieldAlert, Cpu } from 'lucide-react'

function JsonBlock({ value }) {
  const text = useMemo(() => JSON.stringify(value ?? null, null, 2), [value])
  return (
    <pre className="whitespace-pre-wrap rounded-xl bg-black/25 p-4 font-mono text-[12px] leading-relaxed text-slate-100/85 ring-1 ring-white/10 overflow-auto max-h-[500px] custom-scrollbar">
      {text}
    </pre>
  )
}

function parseReport(reportText) {
  if (!reportText) return []
  const sectionHeaders = [
    { id: 'subject_info', title: 'Subject Information', header: 'Subject Information' },
    { id: 'executive_summary', title: 'Executive Summary', header: 'Executive Summary' },
    { id: 'timeline', title: 'Timeline of Material Events', header: 'Timeline of Material Events' },
    { id: 'aml_guidance', title: 'Retrieved AML Guidance', header: 'Retrieved AML Guidance' },
    { id: 'transaction_profile', title: 'Transaction Profile', header: 'Transaction Profile' },
    { id: 'risk_assessment', title: 'Risk Assessment', header: 'Risk Assessment' },
    { id: 'shap', title: 'SHAP Explainability', header: 'SHAP Explainability' },
    { id: 'narrative', title: 'Suspicious Activity Narrative', header: 'Suspicious Activity Narrative' },
    { id: 'key_evidence', title: 'Key Evidence', header: 'Key Evidence' },
    { id: 'recommended_action', title: 'Recommended Action', header: 'Recommended Action' }
  ]

  let currentSection = { id: 'general', title: 'General Overview', content: '' }
  const parsedSections = [currentSection]
  
  const lines = reportText.split('\n')
  for (const line of lines) {
    const matchedSection = sectionHeaders.find(s => line.trim() === s.header)
    if (matchedSection) {
      currentSection = { ...matchedSection, content: '' }
      parsedSections.push(currentSection)
    } else {
      currentSection.content += line + '\n'
    }
  }

  // trim content
  parsedSections.forEach(s => s.content = s.content.trim())
  return parsedSections.filter(s => s.content)
}

export default function Reports() {
  const [subject, setSubject] = useState('ACC-0042')
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('general')

  async function onAnalyze() {
    if (!file) return
    setBusy(true)
    setError('')
    try {
      const res = await analyzeCsv({ file, subjectAccount: subject })
      setResult(res)
      setActiveTab('general')
    } catch (e) {
      setError(e?.message || 'Analysis failed')
      setResult(null)
    } finally {
      setBusy(false)
    }
  }

  const reportText = result?.result?.formatted_report
  const parsedSections = useMemo(() => parseReport(reportText), [reportText])

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

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="glass-strong soft-neu flex flex-col gap-4 rounded-2xl border border-white/[0.12] p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-white/90">Upload Dataset</div>
              <div className="mono mt-0.5 text-[11px] text-slate-200/60">CSV only • header required</div>
            </div>
            <div className="grid h-10 w-10 place-items-center rounded-2xl bg-nexus-violet/[0.12] ring-1 ring-nexus-violet/20">
              <Sparkles className="h-4 w-4 text-violet-200" />
            </div>
          </div>

          <div className="flex flex-col gap-3">
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
              <div className="flex items-center justify-between gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-4 hover:bg-white/[0.07] portal-hover">
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-white/85">{file ? file.name : 'Choose file…'}</div>
                  <div className="mono mt-1 truncate text-[11px] text-slate-200/55">
                    {file ? `${Math.round(file.size / 1024)} KB` : 'Expected columns: amount, location, time, risk_score'}
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
              className="group portal-hover relative inline-flex w-full items-center justify-center gap-3 overflow-hidden rounded-2xl bg-white/10 px-4 py-3 text-sm font-semibold text-white ring-1 ring-white/[0.15] hover:bg-white/[0.14] disabled:cursor-not-allowed disabled:opacity-50"
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

        <div className="glass-strong soft-neu flex min-h-0 flex-col rounded-2xl border border-white/[0.12] p-4 overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-sm font-semibold text-white/90">Analysis Output</div>
              <div className="mono mt-0.5 text-[11px] text-slate-200/60">SAR Report Details</div>
            </div>
            {result?.result?.status && (
              <div className="rounded-full bg-nexus-neon/10 px-3 py-1 text-[11px] font-semibold text-nexus-neon ring-1 ring-nexus-neon/30">
                {result.result.status}
              </div>
            )}
          </div>

          {!result ? (
            <div className="flex flex-1 flex-col items-center justify-center rounded-xl border border-dashed border-white/10 bg-white/[0.02] p-8 text-center">
              <FileText className="mb-3 h-8 w-8 text-white/20" />
              <div className="text-sm font-medium text-white/60">No report generated yet</div>
              <div className="mt-1 text-[12px] text-white/40">Upload a dataset and run analysis to view the SAR report</div>
            </div>
          ) : (
            <div className="flex flex-1 flex-col overflow-hidden">
              <div className="mb-4 flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
                {parsedSections.map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveTab(section.id)}
                    className={`portal-hover flex whitespace-nowrap items-center gap-2 rounded-lg px-4 py-2 text-[12px] font-medium transition-all ${
                      activeTab === section.id
                        ? 'bg-nexus-neon/10 text-nexus-neon ring-1 ring-nexus-neon/30'
                        : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    {section.title}
                  </button>
                ))}
                <button
                  onClick={() => setActiveTab('json_trace')}
                  className={`portal-hover flex whitespace-nowrap items-center gap-2 rounded-lg px-4 py-2 text-[12px] font-medium transition-all ${
                    activeTab === 'json_trace'
                      ? 'bg-nexus-violet/10 text-nexus-violet ring-1 ring-nexus-violet/30'
                      : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  <Cpu className="h-3.5 w-3.5" />
                  JSON Trace
                </button>
              </div>

              <div className="flex-1 overflow-y-auto rounded-xl bg-black/20 p-5 ring-1 ring-white/5 custom-scrollbar">
                <AnimatePresence mode="wait">
                  {activeTab === 'json_trace' ? (
                    <motion.div
                      key="json_trace"
                      initial={{ opacity: 0, y: 5 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -5 }}
                      transition={{ duration: 0.2 }}
                      className="flex flex-col gap-4"
                    >
                      <div>
                        <div className="mono mb-2 text-[11px] text-slate-200/65 flex items-center gap-2">
                          <Activity className="h-3 w-3" /> Full Result Object
                        </div>
                        <JsonBlock value={result?.result} />
                      </div>
                      <div>
                        <div className="mono mb-2 text-[11px] text-slate-200/65 flex items-center gap-2">
                          <ShieldAlert className="h-3 w-3" /> Execution Metadata
                        </div>
                        <JsonBlock value={result?.metadata} />
                      </div>
                    </motion.div>
                  ) : (
                    parsedSections.map((section) => (
                      section.id === activeTab && (
                        <motion.div
                          key={section.id}
                          initial={{ opacity: 0, y: 5 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -5 }}
                          transition={{ duration: 0.2 }}
                          className="prose prose-invert max-w-none"
                        >
                          <h3 className="mb-4 text-lg font-bold text-white/90 border-b border-white/10 pb-2">
                            {section.title}
                          </h3>
                          <div className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed text-slate-200/80">
                            {section.content}
                          </div>
                        </motion.div>
                      )
                    ))
                  )}
                </AnimatePresence>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}
