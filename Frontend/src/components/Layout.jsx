import { Suspense, lazy, useEffect, useMemo, useRef } from 'react'
import { motion } from 'framer-motion'
import Sidebar from './Sidebar.jsx'

const Background3D = lazy(() => import('./SceneBackground.jsx'))

function useMouseLight() {
  const ref = useRef(null)
  const rafRef = useRef(0)
  const latest = useRef({ x: 0, y: 0 })

  useEffect(() => {
    const el = ref.current
    if (!el) return

    const onMove = (e) => {
      const r = el.getBoundingClientRect()
      const x = (e.clientX - r.left) / r.width
      const y = (e.clientY - r.top) / r.height
      latest.current = { x, y }
      if (rafRef.current) return
      rafRef.current = window.requestAnimationFrame(() => {
        rafRef.current = 0
        el.style.setProperty('--mx', String(latest.current.x))
        el.style.setProperty('--my', String(latest.current.y))
      })
    }

    el.addEventListener('mousemove', onMove)
    return () => {
      el.removeEventListener('mousemove', onMove)
      if (rafRef.current) window.cancelAnimationFrame(rafRef.current)
    }
  }, [])

  return ref
}

export default function Layout({ active, onChange, children }) {
  const wrapRef = useMouseLight()
  const overlays = useMemo(
    () => (
      <>
        <div className="pointer-events-none absolute inset-0 opacity-[0.8]">
          <div
            className="absolute -inset-24 blur-2xl"
            style={{
              background:
                'radial-gradient(800px 450px at calc(var(--mx,0.25)*100%) calc(var(--my,0.2)*100%), rgba(79,209,255,0.16), transparent 60%)',
            }}
          />
          <div
            className="absolute -inset-24 blur-2xl"
            style={{
              background:
                'radial-gradient(800px 520px at calc(var(--mx,0.7)*100%) calc(var(--my,0.55)*100%), rgba(139,92,246,0.14), transparent 62%)',
            }}
          />
        </div>
        <div className="pointer-events-none absolute inset-0 [mask-image:radial-gradient(white,transparent_70%)] opacity-20">
          <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.10)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.08)_1px,transparent_1px)] bg-[size:54px_54px]" />
        </div>
      </>
    ),
    [],
  )

  return (
    <div ref={wrapRef} className="relative h-full w-full overflow-hidden">
      <Suspense fallback={null}>
        <Background3D />
      </Suspense>

      {overlays}

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
        className="relative z-10 mx-auto flex h-full max-w-[1400px] gap-5 px-4 py-5 md:px-6"
      >
        <Sidebar active={active} onChange={onChange} />
        <main className="flex min-w-0 flex-1 flex-col">{children}</main>
      </motion.div>
    </div>
  )
}

