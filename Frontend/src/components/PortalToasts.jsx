/* eslint-disable react-refresh/only-export-components */
import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { CheckCircle2, Info, XCircle } from 'lucide-react'

const ToastCtx = createContext(null)

function iconFor(type) {
  if (type === 'success') return CheckCircle2
  if (type === 'error') return XCircle
  return Info
}

function stylesFor(type) {
  if (type === 'success') return 'border-portal-accent/25 bg-portal-accent/10 text-portal-accent'
  if (type === 'error') return 'border-portal-danger/25 bg-portal-danger/10 text-portal-danger'
  return 'border-portal-accent2/25 bg-portal-accent2/10 text-portal-accent2'
}

export function ToastProvider({ children }) {
  const [items, setItems] = useState([])

  const push = useCallback((message, type = 'success') => {
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`
    setItems((prev) => [...prev, { id, message, type }])
    window.setTimeout(() => {
      setItems((prev) => prev.filter((t) => t.id !== id))
    }, 3500)
  }, [])

  const value = useMemo(() => ({ push }), [push])

  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed right-6 top-20 z-[200] flex w-[320px] flex-col gap-2">
        <AnimatePresence initial={false}>
          {items.map((t) => {
            const Icon = iconFor(t.type)
            return (
              <motion.div
                key={t.id}
                initial={{ opacity: 0, x: 40 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 40 }}
                transition={{ duration: 0.25 }}
                className={`pointer-events-none flex items-center gap-3 rounded-xl border px-4 py-3 backdrop-blur-xl ${stylesFor(t.type)}`}
              >
                <Icon className="h-4.5 w-4.5" />
                <div className="text-[13px]">{t.message}</div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </ToastCtx.Provider>
  )
}

export function useToasts() {
  const ctx = useContext(ToastCtx)
  if (!ctx) throw new Error('useToasts must be used within ToastProvider')
  return ctx
}

