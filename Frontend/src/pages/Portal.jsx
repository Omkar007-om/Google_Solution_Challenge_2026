import { useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import SceneBackground from '../components/SceneBackground.jsx'
import { ToastProvider, useToasts } from '../components/PortalToasts.jsx'
import { analyzeCsv, getAnyToken, login, me, setSessionToken, setToken } from '../lib/api.js'
import {
  Bolt,
  CloudUpload,
  FileText,
  Fingerprint,
  FolderOpen,
  LockKeyhole,
  LogOut,
  ShieldHalf,
  User,
  X,
  Activity,
  ShieldAlert,
  Cpu,
} from 'lucide-react'

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

function Navbar({ username, authed, onLogout }) {
  return (
    <nav
      className="portal-hover fixed left-0 top-0 z-[100] w-full border-b border-white/10 bg-black/40 px-4 py-4 backdrop-blur-xl md:px-8"
    >
      <div className="mx-auto flex max-w-[1180px] items-center justify-between">
        <div className="flex items-center gap-3 font-semibold tracking-[0.2em] text-portal-fg/90 uppercase">
          <div className="relative grid h-9 w-9 place-items-center border-2 border-portal-accent text-portal-accent">
            <ShieldHalf className="h-4 w-4" />
            <div className="pointer-events-none absolute -inset-1 border border-portal-accent/20" />
          </div>
          <span>SAR Intel</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="hidden items-center gap-2 font-mono text-[10px] tracking-[0.14em] text-portal-accent md:flex">
            <span className="relative inline-flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-portal-accent/40" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-portal-accent" />
            </span>
            SECURE CHANNEL
          </div>

          {authed ? (
            <>
              <div className="hidden items-center gap-2 text-[13px] text-portal-muted md:flex">
                <div className="grid h-8 w-8 place-items-center rounded-full border border-portal-accent/60 text-portal-accent">
                  <User className="h-4 w-4" />
                </div>
                <span className="font-medium text-portal-fg/80">{username}</span>
              </div>
              <button
                type="button"
                onClick={onLogout}
                className="portal-hover inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.14em] text-portal-muted hover:border-portal-danger/60 hover:text-portal-danger"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </button>
            </>
          ) : null}
        </div>
      </div>
    </nav>
  )
}

function LoginCard({ onAuthed }) {
  const { push } = useToasts()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [remember, setRemember] = useState(true)
  const [busy, setBusy] = useState(false)
  const [uErr, setUErr] = useState('')
  const [pErr, setPErr] = useState('')

  async function onSubmit(e) {
    e.preventDefault()
    const u = username.trim()
    const p = password.trim()
    setUErr(u ? '' : 'Agent ID is required')
    setPErr(p ? '' : 'Access key is required')
    if (!u || !p) {
      push('Please fill in all fields.', 'error')
      return
    }

    setBusy(true)
    try {
      const res = await login({ username: u, password: p })
      if (remember) {
        setToken(res.access_token)
        setSessionToken('')
      } else {
        setSessionToken(res.access_token)
        setToken('')
      }
      await me()
      push(`Welcome, ${u}. Session initialized.`, 'success')
      onAuthed?.(u)
    } catch (err) {
      setToken('')
      setSessionToken('')
      push(err?.message || 'Authentication failed', 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex min-h-screen w-full items-center justify-center px-5 py-10">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="portal-card relative w-full max-w-[420px] overflow-hidden px-10 py-12 text-center"
      >
        <div className="pointer-events-none absolute inset-x-0 top-0 h-px opacity-0 transition-opacity duration-300 hover:opacity-100 portal-accent-line" />

        <div className="mx-auto mb-7 grid h-16 w-16 place-items-center rounded-2xl bg-portal-accent/10 text-portal-accent ring-1 ring-portal-accent/15">
          <Fingerprint className="h-7 w-7" />
        </div>
        <h1 className="text-[26px] font-bold tracking-[-0.5px] text-portal-fg">Secure Access</h1>
        <p className="mt-2 text-[14px] leading-relaxed text-portal-muted">
          Authenticate to access the Suspicious Activity Report portal and upload datasets for analysis.
        </p>

        <form onSubmit={onSubmit} className="mt-9 text-left">
          <div className="mb-5">
            <label className="mb-2 block font-mono text-[10px] uppercase tracking-[0.18em] text-portal-muted">
              Agent ID
            </label>
            <input
              value={username}
              onChange={(e) => {
                setUsername(e.target.value)
                setUErr('')
              }}
              className={`portal-hover w-full rounded-lg bg-white/[0.04] px-4 py-3 text-[14px] text-portal-fg outline-none ring-1 ${
                uErr ? 'ring-portal-danger/60' : 'ring-white/15'
              } focus:ring-portal-accent/70`}
              placeholder="Enter your agent identifier"
              autoComplete="username"
              autoFocus
            />
            {uErr ? <div className="mt-2 font-mono text-[11px] text-portal-danger">{uErr}</div> : null}
          </div>

          <div className="mb-5">
            <label className="mb-2 block font-mono text-[10px] uppercase tracking-[0.18em] text-portal-muted">
              Access Key
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                setPErr('')
              }}
              className={`portal-hover w-full rounded-lg bg-white/[0.04] px-4 py-3 text-[14px] text-portal-fg outline-none ring-1 ${
                pErr ? 'ring-portal-danger/60' : 'ring-white/15'
              } focus:ring-portal-accent/70`}
              placeholder="Enter your access key"
              autoComplete="current-password"
            />
            {pErr ? <div className="mt-2 font-mono text-[11px] text-portal-danger">{pErr}</div> : null}
          </div>

          <div className="mb-7 flex items-center justify-between">
            <label className="portal-hover flex items-center gap-2 text-[13px] text-portal-muted">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="h-4 w-4 accent-portal-accent"
              />
              Remember session
            </label>
            <button
              type="button"
              onClick={() => push('Contact your security administrator for key recovery.', 'info')}
              className="portal-hover text-[12px] text-portal-accent hover:opacity-80"
            >
              Forgot key?
            </button>
          </div>

          <button
            type="submit"
            disabled={busy}
            className="portal-hover inline-flex w-full items-center justify-center gap-2 rounded-lg bg-portal-accent px-4 py-4 text-[14px] font-bold uppercase tracking-[0.12em] text-portal-bg hover:shadow-[0_0_30px_rgba(0,255,136,0.3)] disabled:opacity-70"
          >
            {busy ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-black/30 border-t-black" />
                Authenticating…
              </span>
            ) : (
              <span className="inline-flex items-center gap-2">
                <LockKeyhole className="h-4 w-4" />
                Authenticate
              </span>
            )}
          </button>
        </form>

        <div className="mt-7 border-t border-white/10 pt-6 font-mono text-[11px] leading-relaxed text-portal-muted">
          256-bit TLS encrypted | Session isolated | Audit logged
        </div>
      </motion.div>
    </div>
  )
}

function FileRow({ item, onRemove }) {
  const ext = item.ext.toUpperCase()
  const tone =
    item.ext === 'csv'
      ? 'bg-portal-accent/10 text-portal-accent'
      : item.ext === 'json'
        ? 'bg-violet-500/10 text-violet-300'
        : 'bg-white/[0.04] text-portal-muted'

  return (
    <div className="portal-hover flex items-center gap-4 rounded-xl border border-white/10 bg-white/[0.04] px-5 py-4 backdrop-blur-xl">
      <div className={`grid h-11 w-11 place-items-center rounded-xl ring-1 ring-white/10 ${tone}`}>
        <FileText className="h-5 w-5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="truncate text-[13px] font-medium text-portal-fg/90">{item.name}</div>
        <div className="mt-0.5 font-mono text-[10px] tracking-wide text-portal-muted">
          {item.sizeLabel} · .{ext}
        </div>
        <div className="mt-2 h-[3px] w-full overflow-hidden rounded bg-white/[0.06]">
          <div
            className={`${item.status === 'done' ? 'bg-portal-accent' : 'bg-portal-accent2'} h-full transition-[width]`}
            style={{ width: `${item.progress}%` }}
          />
        </div>
      </div>
      <div className="shrink-0 font-mono text-[10px] tracking-wide text-portal-muted">
        {item.status === 'uploading' ? `Uploading ${Math.round(item.progress)}%` : 'Ready'}
      </div>
      <button
        type="button"
        onClick={() => onRemove(item.id)}
        className="portal-hover rounded-lg p-2 text-portal-muted hover:text-portal-danger"
        aria-label="Remove file"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

function UploadPage({ username, onLogout }) {
  const { push } = useToasts()
  const [files, setFiles] = useState([])
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [showJson, setShowJson] = useState(false)
  const [activeTab, setActiveTab] = useState('general')

  const totals = useMemo(() => {
    const done = files.filter((f) => f.status === 'done')
    const totalBytes = done.reduce((s, f) => s + f.size, 0)
    return { ready: done.length, totalBytes }
  }, [files])

  function fmtSize(bytes) {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  function addFiles(list) {
    const arr = Array.from(list || [])
    let added = 0
    for (const f of arr) {
      const ext = (f.name.split('.').pop() || '').toLowerCase()
      if (ext !== 'csv') {
        push(`"${f.name}" — only .csv is supported for analysis`, 'error')
        continue
      }
      const dup = files.some((x) => x.name === f.name && x.size === f.size)
      if (dup) {
        push(`"${f.name}" — already added`, 'info')
        continue
      }
      const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`
      const item = {
        id,
        file: f,
        name: f.name,
        size: f.size,
        sizeLabel: fmtSize(f.size),
        ext,
        progress: 0,
        status: 'uploading',
      }
      added++
      setFiles((prev) => [...prev, item])

      // simulate upload progress UI only
      let p = 0
      const iv = window.setInterval(() => {
        p += Math.random() * 18 + 6
        setFiles((prev) =>
          prev.map((x) => {
            if (x.id !== id) return x
            const done = p >= 100
            return { ...x, progress: Math.min(100, p), status: done ? 'done' : 'uploading' }
          }),
        )
        if (p >= 100) window.clearInterval(iv)
      }, 180 + Math.random() * 180)
    }
    if (added) push(`${added} file(s) queued.`, 'success')
  }

  function removeFile(id) {
    setFiles((prev) => prev.filter((f) => f.id !== id))
    push('File removed.', 'info')
  }

  async function runAnalysis() {
    const ready = files.filter((f) => f.status === 'done')
    if (!ready.length) return
    setBusy(true)
    setResult(null)
    try {
      // backend supports single CSV; analyze the first ready file
      const res = await analyzeCsv({ file: ready[0].file, subjectAccount: username })
      setResult(res)
      push('SAR analysis completed.', 'success')
    } catch (e) {
      push(e?.message || 'Analysis failed', 'error')
    } finally {
      setBusy(false)
    }
  }

  const reportText = result?.result?.formatted_report
  const parsedSections = useMemo(() => parseReport(reportText), [reportText])

  return (
    <div className="w-full px-5 pb-12 pt-[100px]">
      <div className="mx-auto w-full max-w-[980px]">
        <div className="mb-10">
          <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-portal-accent">Dataset Upload</div>
          <div className="mt-3 text-4xl font-bold tracking-[-1px] text-portal-fg">Upload SAR Data</div>
          <div className="mt-2 text-[15px] leading-relaxed text-portal-muted">
            Drag and drop your transaction datasets below. Files are validated before processing.
          </div>
        </div>

        <div className="portal-card overflow-hidden p-0">
          <DropZone onFiles={addFiles} disabled={busy} />
        </div>

        {files.length ? (
          <div className="mt-8">
            <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.18em] text-portal-muted">
              Uploaded Files
            </div>
            <div className="flex flex-col gap-3">
              {files.map((f) => (
                <FileRow key={f.id} item={f} onRemove={removeFile} />
              ))}
            </div>
          </div>
        ) : null}

        {files.length ? (
          <div className="mt-8 flex flex-wrap items-center justify-between gap-4">
            <div className="text-[13px] text-portal-muted">
              <span className="font-semibold text-portal-fg">{totals.ready}</span> files ready ·{' '}
              <span className="font-semibold text-portal-fg">{fmtSize(totals.totalBytes)}</span> total
            </div>
            <button
              type="button"
              onClick={runAnalysis}
              disabled={!totals.ready || busy}
              className="portal-hover inline-flex items-center gap-2 rounded-lg bg-portal-accent px-8 py-3 text-[13px] font-bold uppercase tracking-[0.12em] text-portal-bg hover:shadow-[0_0_30px_rgba(0,255,136,0.3)] disabled:opacity-30"
            >
              {busy ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-black/30 border-t-black" /> : <Bolt className="h-4 w-4" />}
              Run Analysis
            </button>
          </div>
        ) : null}

        {result ? (
          <div className="mt-10 grid grid-cols-1 gap-4">
            <div className="portal-card flex min-h-0 flex-col p-5 overflow-hidden">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-portal-muted">SAR Narrative Report</div>
                  <div className="mono mt-0.5 text-[11px] text-slate-200/60">Parsed Report Sections</div>
                </div>
                {result?.result?.status && (
                  <div className="rounded-full bg-portal-accent/10 px-3 py-1 text-[11px] font-semibold text-portal-accent ring-1 ring-portal-accent/30">
                    {result.result.status}
                  </div>
                )}
              </div>

              <div className="flex flex-1 flex-col overflow-hidden">
                <div className="mb-4 flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
                  {parsedSections.map((section) => (
                    <button
                      key={section.id}
                      onClick={() => setActiveTab(section.id)}
                      className={`portal-hover flex whitespace-nowrap items-center gap-2 rounded-lg px-4 py-2 text-[12px] font-medium transition-all ${
                        activeTab === section.id
                          ? 'bg-portal-accent/10 text-portal-accent ring-1 ring-portal-accent/30'
                          : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'
                      }`}
                    >
                      {section.title}
                    </button>
                  ))}
                </div>

                <div className="flex-1 overflow-y-auto rounded-xl bg-black/20 p-5 ring-1 ring-white/5 custom-scrollbar min-h-[300px] max-h-[500px]">
                  <AnimatePresence mode="wait">
                    {parsedSections.map((section) => (
                      section.id === activeTab && (
                        <motion.div
                          key={section.id}
                          initial={{ opacity: 0, y: 5 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, y: -5 }}
                          transition={{ duration: 0.2 }}
                          className="max-w-none"
                        >
                          <h3 className="mb-4 text-lg font-bold text-white/90 border-b border-white/10 pb-2">
                            {section.title}
                          </h3>
                          <div className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed text-slate-200/80">
                            {section.content}
                          </div>
                        </motion.div>
                      )
                    ))}
                  </AnimatePresence>
                </div>
              </div>
            </div>
            
            <div className="portal-card p-5">
              <div className="mb-3 flex items-center justify-between gap-3">
                <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-portal-muted">Case Details & Trace</div>
                <button
                  type="button"
                  onClick={() => setShowJson((v) => !v)}
                  className="portal-hover rounded-md border border-white/10 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.12em] text-portal-muted hover:text-portal-accent hover:border-portal-accent/40"
                >
                  {showJson ? 'Hide Raw JSON' : 'Show Raw JSON'}
                </button>
              </div>
              <div className="rounded-xl bg-black/30 p-4 ring-1 ring-white/10">
                <div className="grid grid-cols-1 gap-2 text-[12px] text-portal-fg/85 sm:grid-cols-2">
                  <div><span className="text-portal-muted">Report ID:</span> {result?.result?.report_id || '-'}</div>
                  <div><span className="text-portal-muted">Subject:</span> {result?.result?.subject_information?.subject_account || '-'}</div>
                  <div><span className="text-portal-muted">Risk Level:</span> {result?.result?.risk_assessment?.level || '-'}</div>
                  <div><span className="text-portal-muted">Risk Score:</span> {result?.result?.risk_assessment?.score ?? '-'}</div>
                  <div><span className="text-portal-muted">Decision:</span> {result?.result?.review_decision?.decision || '-'}</div>
                  <div><span className="text-portal-muted">Action:</span> {result?.result?.investigator_reasoning?.recommended_action || '-'}</div>
                </div>
              </div>
              {showJson ? (
                <div className="mt-3 flex flex-col gap-3">
                  <div className="font-mono text-[11px] text-slate-200/65 flex items-center gap-2">
                    <Activity className="h-3 w-3" /> Full Result Object
                  </div>
                  <pre className="whitespace-pre-wrap rounded-xl bg-black/30 p-4 font-mono text-[12px] leading-relaxed text-portal-fg/85 ring-1 ring-white/10 overflow-auto max-h-[500px] custom-scrollbar">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                  
                  <div className="font-mono text-[11px] text-slate-200/65 flex items-center gap-2 mt-2">
                    <ShieldAlert className="h-3 w-3" /> Execution Metadata
                  </div>
                  <pre className="whitespace-pre-wrap rounded-xl bg-black/30 p-4 font-mono text-[12px] leading-relaxed text-portal-fg/85 ring-1 ring-white/10 overflow-auto max-h-[500px] custom-scrollbar">
                    {JSON.stringify(result.metadata, null, 2)}
                  </pre>
                </div>
              ) : null}
            </div>
          </div>
        ) : null}

        <div className="mt-10 flex justify-end">
          <button
            type="button"
            onClick={onLogout}
            className="portal-hover inline-flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2 font-mono text-[10px] uppercase tracking-[0.14em] text-portal-muted hover:border-portal-danger/60 hover:text-portal-danger"
          >
            <LogOut className="h-4 w-4" />
            Terminate Session
          </button>
        </div>
      </div>
    </div>
  )
}

function DropZone({ onFiles, disabled }) {
  const { push } = useToasts()
  const [drag, setDrag] = useState(false)
  const inputRef = useRef(null)

  return (
    <div
      className={`portal-hover relative cursor-pointer rounded-2xl border-2 border-dashed px-10 py-16 text-center transition ${
        drag ? 'border-portal-accent bg-portal-accent/5 shadow-[0_0_40px_rgba(0,255,136,0.06)]' : 'border-white/15 bg-white/[0.03]'
      }`}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault()
        if (disabled) return
        setDrag(true)
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault()
        setDrag(false)
        if (disabled) return
        const fl = e.dataTransfer?.files
        if (fl?.length) onFiles?.(fl)
      }}
    >
      <div
        className={`mx-auto mb-6 grid h-[72px] w-[72px] place-items-center rounded-full bg-portal-accent/10 text-portal-accent transition ${
          drag ? 'scale-110 shadow-[0_0_30px_rgba(0,255,136,0.2)]' : ''
        }`}
      >
        <CloudUpload className="h-7 w-7" />
      </div>
      <div className="text-lg font-semibold text-portal-fg">Drop files here</div>
      <div className="mt-2 text-[13px] text-portal-muted">
        or <span className="text-portal-accent underline">browse</span> from your local system
      </div>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          inputRef.current?.click()
        }}
        className="portal-hover mt-6 inline-flex items-center gap-2 rounded-lg border border-portal-accent px-6 py-3 text-[13px] font-semibold text-portal-accent hover:bg-portal-accent/10 hover:shadow-[0_0_20px_rgba(0,255,136,0.1)]"
      >
        <FolderOpen className="h-4.5 w-4.5" />
        Browse Files
      </button>
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        {['.CSV'].map((b) => (
          <span
            key={b}
            className="rounded border border-white/10 bg-white/[0.03] px-3 py-1 font-mono text-[10px] tracking-wide text-portal-muted"
          >
            {b}
          </span>
        ))}
      </div>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        multiple
        disabled={disabled}
        className="hidden"
        onChange={(e) => {
          const fl = e.target.files
          if (fl?.length) onFiles?.(fl)
          e.target.value = ''
        }}
      />
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          push('CSV only for backend analysis in this build.', 'info')
        }}
        className="portal-hover pointer-events-auto absolute right-4 top-4 rounded-lg border border-white/10 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.14em] text-portal-muted hover:border-white/20"
      >
        Help
      </button>
    </div>
  )
}

function PortalInner() {
  const [authed, setAuthed] = useState(() => Boolean(getAnyToken()))
  const [username, setUsername] = useState('')

  useEffect(() => {
    const t = getAnyToken()
    if (!t) return
    me()
      .then((r) => {
        setAuthed(true)
        setUsername(r?.username || 'agent')
      })
      .catch(() => setAuthed(false))
  }, [])

  const onLogout = () => {
    setToken('')
    setSessionToken('')
    setAuthed(false)
    setUsername('')
  }

  return (
    <div className="relative min-h-screen w-full">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <SceneBackground />
      </div>
      <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
        <motion.div
          className="absolute -left-40 top-20 h-[380px] w-[380px] rounded-full bg-cyan-400/10 blur-3xl"
          animate={{ x: [0, 90, -40, 0], y: [0, -30, 40, 0], scale: [1, 1.08, 0.95, 1] }}
          transition={{ duration: 22, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute right-[-120px] top-[24%] h-[420px] w-[420px] rounded-full bg-violet-500/12 blur-3xl"
          animate={{ x: [0, -100, 35, 0], y: [0, 55, -25, 0], scale: [1, 0.94, 1.06, 1] }}
          transition={{ duration: 26, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute bottom-[-120px] left-[22%] h-[360px] w-[360px] rounded-full bg-emerald-400/10 blur-3xl"
          animate={{ x: [0, 40, -70, 0], y: [0, -60, 20, 0], scale: [1, 1.05, 0.93, 1] }}
          transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>
      <div className="pointer-events-none fixed inset-0 z-[1] scanlines opacity-100" />

      <Navbar username={username} authed={authed} onLogout={onLogout} />

      <AnimatePresence mode="wait">
        {!authed ? (
          <motion.div key="login" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <LoginCard
              onAuthed={(u) => {
                setAuthed(true)
                setUsername(u)
              }}
            />
          </motion.div>
        ) : (
          <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <UploadPage username={username} onLogout={onLogout} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default function Portal() {
  return (
    <ToastProvider>
      <PortalInner />
    </ToastProvider>
  )
}

