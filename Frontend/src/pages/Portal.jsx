import { useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ToastProvider, useToasts } from '../components/PortalToasts.jsx'
import FinanceBackground from '../components/FinanceBackground.jsx'
import { analyzeCsv, getAnyToken, login, me, setSessionToken, setToken } from '../lib/api.js'
import {
  Bolt,
  CloudUpload,
  FileText,
  Fingerprint,
  FolderOpen,
  LockKeyhole,
  LogOut,
  X,
  Activity,
  ShieldAlert,
  Sparkles, 
  Download, 
  Wand2, 
  BookOpen, 
  ArrowRight, 
  Twitter, 
  Linkedin, 
  Instagram, 
  Menu,
  Plus
} from 'lucide-react'

// Report Parser
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
  parsedSections.forEach(s => s.content = s.content.trim())
  return parsedSections.filter(s => s.content)
}

// ----------------------------------------------------
// COMPONENTS ADAPTED TO GRAYSCALE LIQUID GLASS
// ----------------------------------------------------

function LoginCard({ onAuthed }) {
  const { push } = useToasts()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin')
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
    <div className="w-full text-center text-white">
      <div className="mx-auto mb-7 grid h-16 w-16 place-items-center rounded-2xl bg-white/10 text-white">
        <Fingerprint className="h-7 w-7" />
      </div>
      <h2 className="text-[26px] font-medium tracking-tight">Secure Access</h2>
      <p className="mt-2 text-[14px] leading-relaxed text-white/60">
        Authenticate to access the Suspicious Activity Report portal.
      </p>

      <form onSubmit={onSubmit} className="mt-9 text-left">
        <div className="mb-5">
          <label className="mb-2 block text-xs uppercase tracking-widest text-white/50">Agent ID</label>
          <input
            value={username}
            onChange={(e) => {
              setUsername(e.target.value)
              setUErr('')
            }}
            className="w-full rounded-lg bg-white/10 px-4 py-3 text-[14px] text-white outline-none focus:ring-1 focus:ring-white/50"
            placeholder="Enter your agent identifier"
            autoComplete="username"
            autoFocus
          />
          {uErr && <div className="mt-2 text-[11px] text-red-400">{uErr}</div>}
        </div>

        <div className="mb-5">
          <label className="mb-2 block text-xs uppercase tracking-widest text-white/50">Access Key</label>
          <input
            type="password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value)
              setPErr('')
            }}
            className="w-full rounded-lg bg-white/10 px-4 py-3 text-[14px] text-white outline-none focus:ring-1 focus:ring-white/50"
            placeholder="Enter your access key"
            autoComplete="current-password"
          />
          {pErr && <div className="mt-2 text-[11px] text-red-400">{pErr}</div>}
        </div>

        <div className="mb-7 flex items-center justify-between">
          <label className="flex items-center gap-2 text-[13px] text-white/60 cursor-pointer">
            <input
              type="checkbox"
              checked={remember}
              onChange={(e) => setRemember(e.target.checked)}
              className="h-4 w-4"
            />
            Remember session
          </label>
          <button type="button" className="text-[12px] text-white/80 hover:text-white transition-colors">
            Forgot key?
          </button>
        </div>

        <button
          type="submit"
          disabled={busy}
          className="liquid-glass inline-flex w-full items-center justify-center gap-2 rounded-lg px-4 py-4 text-[14px] font-medium tracking-wide hover:scale-[1.02] active:scale-[0.98] transition-transform disabled:opacity-70"
        >
          {busy ? (
            <span className="inline-flex items-center gap-2">
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
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
    </div>
  )
}

function DropZone({ onFiles, disabled }) {
  const { push } = useToasts()
  const [drag, setDrag] = useState(false)
  const inputRef = useRef(null)

  return (
    <div
      className={`relative cursor-pointer rounded-2xl border border-dashed px-10 py-16 text-center transition ${
        drag ? 'border-white bg-white/10' : 'border-white/20 bg-white/5'
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
      <div className={`mx-auto mb-6 grid h-[72px] w-[72px] place-items-center rounded-full bg-white/10 transition ${drag ? 'scale-110' : ''}`}>
        <CloudUpload className="h-7 w-7 text-white" />
      </div>
      <div className="text-lg font-medium text-white">Drop files here</div>
      <div className="mt-2 text-[13px] text-white/60">
        or <span className="text-white underline">browse</span> from your local system
      </div>
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          inputRef.current?.click()
        }}
        className="mt-6 inline-flex items-center gap-2 rounded-lg border border-white/30 px-6 py-3 text-[13px] font-medium text-white hover:bg-white/10 transition-colors"
      >
        <FolderOpen className="h-4 w-4" />
        Browse Files
      </button>
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
    </div>
  )
}

function FileRow({ item, onRemove }) {
  const ext = item.ext.toUpperCase()
  return (
    <div className="flex items-center gap-4 rounded-xl bg-white/5 px-5 py-4">
      <div className="grid h-11 w-11 place-items-center rounded-xl bg-white/10 text-white">
        <FileText className="h-5 w-5" />
      </div>
      <div className="min-w-0 flex-1">
        <div className="truncate text-[13px] font-medium text-white">{item.name}</div>
        <div className="mt-0.5 text-[10px] tracking-wide text-white/50">
          {item.sizeLabel} · .{ext}
        </div>
        <div className="mt-2 h-[3px] w-full overflow-hidden rounded bg-white/10">
          <div
            className="bg-white h-full transition-[width]"
            style={{ width: `${item.progress}%` }}
          />
        </div>
      </div>
      <div className="shrink-0 text-[10px] tracking-wide text-white/50">
        {item.status === 'uploading' ? `Uploading ${Math.round(item.progress)}%` : 'Ready'}
      </div>
      <button
        type="button"
        onClick={() => onRemove(item.id)}
        className="rounded-lg p-2 text-white/50 hover:text-white transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

function UploadPage({ username, onLogout, analysisResult, setAnalysisResult, parsedSections }) {
  const { push } = useToasts()
  const [files, setFiles] = useState([])
  const [busy, setBusy] = useState(false)
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
    for (const f of arr) {
      if (!f.name.toLowerCase().endsWith('.csv')) {
        push(`"${f.name}" — only .csv is supported`, 'error')
        continue
      }
      const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`
      const item = {
        id, file: f, name: f.name, size: f.size, sizeLabel: fmtSize(f.size),
        ext: 'csv', progress: 0, status: 'uploading',
      }
      setFiles((prev) => [...prev, item])
      
      let p = 0
      const iv = window.setInterval(() => {
        p += Math.random() * 20 + 10
        setFiles((prev) => prev.map((x) => {
          if (x.id !== id) return x
          const done = p >= 100
          return { ...x, progress: Math.min(100, p), status: done ? 'done' : 'uploading' }
        }))
        if (p >= 100) window.clearInterval(iv)
      }, 200)
    }
  }

  function removeFile(id) {
    setFiles((prev) => prev.filter((f) => f.id !== id))
  }

  async function runAnalysis() {
    const ready = files.filter((f) => f.status === 'done')
    if (!ready.length) return
    setBusy(true)
    setAnalysisResult(null)
    try {
      const res = await analyzeCsv({ file: ready[0].file, subjectAccount: username })
      setAnalysisResult(res)
    } catch (e) {
      push(e?.message || 'Analysis failed', 'error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="w-full text-white">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-medium tracking-tight">Dataset Upload</h2>
        <div className="mt-2 text-[14px] text-white/60">Upload your CSV transaction logs for analysis.</div>
      </div>

      <DropZone onFiles={addFiles} disabled={busy} />

      {files.length > 0 && (
        <div className="mt-6 flex flex-col gap-3">
          {files.map((f) => <FileRow key={f.id} item={f} onRemove={removeFile} />)}
          
          <div className="mt-4 flex items-center justify-between">
            <div className="text-[13px] text-white/60">{totals.ready} files ready</div>
            <button
              onClick={runAnalysis}
              disabled={!totals.ready || busy}
              className="liquid-glass inline-flex items-center gap-2 rounded-lg px-6 py-3 text-[13px] font-medium hover:bg-white/10 disabled:opacity-50"
            >
              {busy ? <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" /> : <Bolt className="h-4 w-4" />}
              Run Analysis
            </button>
          </div>
        </div>
      )}

      {analysisResult && (
        <div className="mt-8 pt-8 border-t border-white/10">
          <div className="flex items-center gap-2 mb-6 overflow-x-auto custom-scrollbar pb-2">
            {parsedSections.map(s => (
              <button
                key={s.id}
                onClick={() => setActiveTab(s.id)}
                className={`whitespace-nowrap rounded-lg px-4 py-2 text-[12px] font-medium transition-colors ${
                  activeTab === s.id ? 'bg-white/20 text-white' : 'bg-white/5 text-white/60 hover:bg-white/10'
                }`}
              >
                {s.title}
              </button>
            ))}
          </div>
          
          <div className="rounded-xl bg-black/20 p-5 ring-1 ring-white/10 min-h-[300px] max-h-[500px] overflow-y-auto custom-scrollbar">
            <AnimatePresence mode="wait">
              {parsedSections.map(s => s.id === activeTab && (
                <motion.div key={s.id} initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}}>
                  <h3 className="mb-4 text-lg font-medium border-b border-white/10 pb-2">{s.title}</h3>
                  <div className="whitespace-pre-wrap font-mono text-[13px] leading-relaxed text-white/80">{s.content}</div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          <div className="mt-6 flex justify-between items-center">
            <button onClick={() => setShowJson(!showJson)} className="text-xs text-white/50 hover:text-white underline">
              {showJson ? 'Hide Raw JSON' : 'Show Raw JSON'}
            </button>
            <button onClick={onLogout} className="text-xs text-red-400 hover:text-red-300 flex items-center gap-1">
              <LogOut className="w-3 h-3" /> Logout
            </button>
          </div>

          {showJson && (
            <pre className="mt-4 p-4 rounded-xl bg-black/40 text-xs text-white/70 overflow-auto max-h-[300px] custom-scrollbar">
              {JSON.stringify(analysisResult, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}

function PatternRecognitionView({ parsedSections }) {
  if (!parsedSections || parsedSections.length <= 1) {
    return (
      <div className="w-full text-white text-center py-16">
        <Activity size={48} className="mx-auto text-white/20 mb-6" />
        <h2 className="text-2xl font-medium tracking-tight mb-2">Awaiting Dataset</h2>
        <p className="text-white/50 text-sm">Upload a CSV in the Automated Reporting module to analyze patterns.</p>
      </div>
    )
  }

  const riskData = parsedSections.find(s => s.id === 'risk_assessment')?.content || 'No risk assessment found.'
  const shapData = parsedSections.find(s => s.id === 'shap')?.content || 'No SHAP data found.'

  return (
    <div className="w-full text-white">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-medium tracking-tight">Pattern Recognition</h2>
        <div className="mt-2 text-[14px] text-white/60">Live behavioral synthesis & anomaly detection.</div>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
        <div className="liquid-glass rounded-2xl p-6 border border-white/10">
          <h3 className="text-xs uppercase tracking-widest text-white/50 mb-4 flex items-center gap-2">
             <Activity size={14} className="text-white/40" /> Risk Assessment
          </h3>
          <pre className="whitespace-pre-wrap font-mono text-xs text-white/80 leading-relaxed max-h-[250px] overflow-y-auto custom-scrollbar p-2">
            {riskData}
          </pre>
        </div>

        <div className="liquid-glass rounded-2xl p-6 border border-white/10 flex flex-col gap-3">
          <h3 className="text-xs uppercase tracking-widest text-white/50 mb-1 flex items-center gap-2">
             <Bolt size={14} className="text-white/40" /> SHAP Explainability
          </h3>
          <pre className="whitespace-pre-wrap font-mono text-xs text-white/80 leading-relaxed max-h-[250px] overflow-y-auto custom-scrollbar p-2">
            {shapData}
          </pre>
        </div>
      </div>
    </div>
  )
}

function KnowledgeGraphView({ parsedSections }) {
  if (!parsedSections || parsedSections.length <= 1) {
    return (
      <div className="w-full text-white text-center py-16">
        <ShieldAlert size={48} className="mx-auto text-white/20 mb-6" />
        <h2 className="text-2xl font-medium tracking-tight mb-2">Awaiting Dataset</h2>
        <p className="text-white/50 text-sm">Upload a CSV in the Automated Reporting module to build the graph.</p>
      </div>
    )
  }

  const timelineData = parsedSections.find(s => s.id === 'timeline')?.content || 'No timeline available.'
  const profileData = parsedSections.find(s => s.id === 'transaction_profile')?.content || 'No profile available.'

  return (
    <div className="w-full text-white">
      <div className="mb-10 text-center">
        <h2 className="text-3xl font-medium tracking-tight">Knowledge Graph</h2>
        <div className="mt-2 text-[14px] text-white/60">Immutable ledger and transaction routing paths.</div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        <div className="liquid-glass rounded-2xl p-6 border border-white/10 min-h-[300px] flex flex-col gap-4">
          <h3 className="text-xs uppercase tracking-widest text-white/50 mb-2 flex items-center gap-2">
            <Activity size={14} /> Ledger Timeline
          </h3>
          <pre className="whitespace-pre-wrap font-mono text-xs text-white/80 leading-relaxed max-h-[400px] overflow-y-auto custom-scrollbar p-2 relative before:absolute before:top-4 before:bottom-4 before:left-2 before:w-[2px] before:bg-white/5">
            {timelineData}
          </pre>
        </div>

        <div className="liquid-glass rounded-2xl p-6 border border-white/10 min-h-[200px] flex flex-col gap-4">
          <h3 className="text-xs uppercase tracking-widest text-white/50 mb-2 flex items-center gap-2">
            <BookOpen size={14} /> Transaction Profile
          </h3>
          <pre className="whitespace-pre-wrap font-mono text-xs text-white/80 leading-relaxed max-h-[300px] overflow-y-auto custom-scrollbar p-2">
            {profileData}
          </pre>
        </div>
      </div>
    </div>
  )
}

// ----------------------------------------------------
// MAIN BLOOM HERO PAGE
// ----------------------------------------------------

function PortalInner() {
  const [authed, setAuthed] = useState(() => Boolean(getAnyToken()))
  const [username, setUsername] = useState('')
  const [modalView, setModalView] = useState(() => Boolean(getAnyToken()) ? null : 'login')
  const [pendingView, setPendingView] = useState(null)
  
  const [analysisResult, setAnalysisResult] = useState(null)
  const parsedSections = useMemo(() => parseReport(analysisResult?.result?.formatted_report), [analysisResult])

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
    setModalView('login')
  }

  const handleOpenView = (view) => {
    if (!authed) {
      setPendingView(view)
      setModalView('login')
    } else {
      setModalView(view)
    }
  }

  const handleAuthed = (u) => {
    setAuthed(true)
    setUsername(u)
    setModalView(pendingView || 'upload')
    setPendingView(null)
  }

  const closeModal = () => setModalView(null)

  return (
    <main className="relative min-h-screen w-full bg-black overflow-hidden text-white font-sans">
      {/* Finance Data Network 3D Background */}
      <div className="absolute inset-0 z-0">
        <FinanceBackground />
      </div>

      {/* Main Content Layout */}
      <div className="relative z-10 flex flex-row min-h-screen w-full">
        
        {/* Left Panel (52%) */}
        <div className="relative w-full lg:w-[52%] h-screen p-4 lg:p-6 flex flex-col">
          <div className="liquid-glass-strong absolute inset-4 lg:inset-6 rounded-3xl -z-10"></div>
          
          {/* Nav */}
          <nav className="flex justify-between items-center w-full px-4 pt-4">
            <div className="flex items-center gap-3">
              <img 
                src="/logo.png" 
                alt="Nexus Logo" 
                className="w-8 h-8 object-contain"
                onError={(e) => { e.currentTarget.src = "https://placehold.co/32x32/111/FFF?text=N" }}
              />
              <span className="font-semibold text-2xl tracking-widest uppercase">NEXUS</span>
            </div>
            <button className="liquid-glass px-4 py-2 rounded-full flex items-center gap-2 hover:scale-105 transition-transform">
              <span className="text-sm font-medium">Menu</span>
              <Menu size={16} />
            </button>
          </nav>

          {/* Hero Center */}
          <div className="flex-1 flex flex-col items-center justify-center text-center px-6">
            <img 
              src="/logo.png" 
              alt="Nexus Logo Large" 
              className="w-20 h-20 object-contain mb-8"
              onError={(e) => { e.currentTarget.src = "https://placehold.co/80x80/111/FFF?text=N" }}
            />
            <h1 className="text-6xl lg:text-7xl font-medium tracking-[-0.04em] leading-tight mb-10 max-w-2xl">
              Next-Generation <br />
              <span className="text-white/70 italic tracking-tight">SAR Intelligence</span>
            </h1>
            


            <div className="flex flex-wrap justify-center gap-3">
              <span className="liquid-glass px-5 py-2 rounded-full text-xs text-white/80 font-mono">Global Graph</span>
              <span className="liquid-glass px-5 py-2 rounded-full text-xs text-white/80 font-mono">Agent Swarm</span>
              <span className="liquid-glass px-5 py-2 rounded-full text-xs text-white/80 font-mono">Risk Assessment</span>
            </div>
          </div>

          {/* Bottom Quote */}
          <div className="mt-auto px-6 pb-6 text-center lg:text-left">
            <div className="text-[11px] tracking-[0.2em] uppercase text-white/40 mb-3 font-semibold">FINANCIAL SURVEILLANCE</div>
            <div className="text-lg mb-4 text-white/90 font-light">
              "Continuous monitoring of <span className="text-white font-medium italic">high-risk networks</span>."
            </div>
            <div className="flex items-center justify-center lg:justify-start gap-3 text-[10px] text-white/50 uppercase tracking-widest font-semibold">
              <div className="w-8 h-[1px] bg-white/20"></div>
              MULTI-AGENT PIPELINE
              <div className="w-8 h-[1px] bg-white/20"></div>
            </div>
          </div>
        </div>

        {/* Right Panel (48%) - Desktop Only */}
        <div className="hidden lg:flex w-[48%] h-screen p-6 flex-col relative">
          
          {/* Top Bar */}
          <div className="flex justify-between items-center w-full mb-12">
            <div className="liquid-glass rounded-full flex items-center px-2 py-2 gap-2">
              <a href="#" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:text-white/80 transition-colors">
                <Twitter size={14} />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:text-white/80 transition-colors">
                <Linkedin size={14} />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:text-white/80 transition-colors">
                <Instagram size={14} />
              </a>
              <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:text-white/80 transition-colors ml-2">
                <ArrowRight size={14} />
              </button>
            </div>

            <button onClick={() => handleOpenView(authed ? 'upload' : 'login')} className="liquid-glass px-4 py-2 rounded-full flex items-center gap-2 hover:scale-105 transition-transform">
              <Sparkles size={16} />
              <span className="text-sm font-medium font-mono">{authed ? username : 'Login'}</span>
            </button>
          </div>

          {/* Architecture Card */}
          <div className="liquid-glass w-64 rounded-3xl p-6 ml-auto mr-12 hover:scale-[1.02] transition-transform">
            <h3 className="font-semibold text-sm tracking-wide mb-2 uppercase text-white/90">Architecture</h3>
            <p className="text-xs text-white/60 leading-relaxed">
              Powered by a dynamic graph of 7 autonomous AI agents executing KYC, transaction profiling, and FinCEN reporting.
            </p>
          </div>

          {/* Bottom Feature Section */}
          <div className="liquid-glass mt-auto rounded-[2.5rem] p-4 flex flex-col gap-4">
            <div className="flex gap-4">
              <div className="liquid-glass flex-1 rounded-3xl p-6 hover:scale-105 transition-transform cursor-pointer" onClick={() => handleOpenView('pattern')}>
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center mb-4 text-white/80">
                  <Activity size={18} />
                </div>
                <h4 className="font-semibold text-sm tracking-wide mb-1">Pattern Recognition</h4>
                <p className="text-xs text-white/50">Behavioral synthesis</p>
              </div>
              <div className="liquid-glass flex-1 rounded-3xl p-6 hover:scale-105 transition-transform cursor-pointer" onClick={() => handleOpenView('graph')}>
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center mb-4 text-white/80">
                  <ShieldAlert size={18} />
                </div>
                <h4 className="font-semibold text-sm tracking-wide mb-1">Knowledge Graph</h4>
                <p className="text-xs text-white/50">Immutable ledgers</p>
              </div>
            </div>

            <div className="liquid-glass rounded-3xl p-5 flex items-center gap-5 hover:scale-[1.02] transition-transform cursor-pointer" onClick={() => handleOpenView('upload')}>
              <div className="w-20 h-16 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center">
                 <FileText className="text-white/40" size={24} />
              </div>
              <div className="flex-1">
                <h4 className="font-semibold text-sm tracking-wide mb-1">Automated Reporting</h4>
                <p className="text-xs text-white/50">FinCEN-compliant drafting</p>
              </div>
              <button className="liquid-glass w-10 h-10 rounded-full flex items-center justify-center mr-2">
                <Plus size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Modal Overlay */}
      {modalView && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-12">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-md" onClick={closeModal}></div>
          <div className="liquid-glass-strong w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-[2.5rem] relative z-10 p-8 md:p-12 custom-scrollbar">
            <button 
              onClick={closeModal}
              className="absolute top-6 right-6 w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-colors z-50"
            >
              <X size={20} />
            </button>
            
            <AnimatePresence mode="wait">
              {modalView === 'login' && (
                <motion.div key="login" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <LoginCard onAuthed={handleAuthed} />
                </motion.div>
              )}
              {modalView === 'upload' && (
                <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <UploadPage 
                    username={username} 
                    onLogout={onLogout} 
                    analysisResult={analysisResult} 
                    setAnalysisResult={setAnalysisResult} 
                    parsedSections={parsedSections} 
                  />
                </motion.div>
              )}
              {modalView === 'pattern' && (
                <motion.div key="pattern" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <PatternRecognitionView parsedSections={parsedSections} />
                </motion.div>
              )}
              {modalView === 'graph' && (
                <motion.div key="graph" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <KnowledgeGraphView parsedSections={parsedSections} />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      )}
    </main>
  )
}

export default function Portal() {
  return (
    <ToastProvider>
      <PortalInner />
    </ToastProvider>
  )
}
