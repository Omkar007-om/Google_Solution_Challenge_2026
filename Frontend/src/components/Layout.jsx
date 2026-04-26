import { Suspense, lazy } from 'react'
import { motion } from 'framer-motion'
import Sidebar from './Sidebar.jsx'

const Background3D = lazy(() => import('./SceneBackground.jsx'))

export default function Layout({ active, onChange, children }) {
  return (
    <div className="relative h-full w-full overflow-hidden">
      <Suspense fallback={null}>
        <Background3D />
      </Suspense>

      <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-[0.8]">
        <motion.div
          className="absolute -left-28 top-10 h-[340px] w-[340px] rounded-full bg-cyan-400/15 blur-3xl"
          animate={{ x: [0, 60, -30, 0], y: [0, -20, 35, 0], scale: [1, 1.06, 0.95, 1] }}
          transition={{ duration: 20, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="absolute right-[-100px] top-[28%] h-[390px] w-[390px] rounded-full bg-violet-500/15 blur-3xl"
          animate={{ x: [0, -80, 25, 0], y: [0, 45, -15, 0], scale: [1, 0.93, 1.04, 1] }}
          transition={{ duration: 24, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>
      <div className="pointer-events-none absolute inset-0 [mask-image:radial-gradient(white,transparent_70%)] opacity-20">
        <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.10)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.08)_1px,transparent_1px)] bg-[size:54px_54px]" />
      </div>

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

