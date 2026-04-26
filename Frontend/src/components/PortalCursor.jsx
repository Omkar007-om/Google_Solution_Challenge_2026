import { useEffect, useRef } from 'react'

export default function PortalCursor() {
  const dotRef = useRef(null)
  const ringRef = useRef(null)
  const state = useRef({ cx: 0, cy: 0, rx: 0, ry: 0 })

  useEffect(() => {
    const dot = dotRef.current
    const ring = ringRef.current
    if (!dot || !ring) return

    const onMove = (e) => {
      state.current.cx = e.clientX
      state.current.cy = e.clientY
    }

    const onOver = (e) => {
      const target = e.target
      if (!(target instanceof Element)) return
      if (target.closest('a,button,input,label,.portal-hover')) ring.classList.add('is-hover')
    }
    const onOut = (e) => {
      const target = e.target
      if (!(target instanceof Element)) return
      if (target.closest('a,button,input,label,.portal-hover')) ring.classList.remove('is-hover')
    }

    document.addEventListener('mousemove', onMove, { passive: true })
    document.addEventListener('mouseover', onOver, { passive: true })
    document.addEventListener('mouseout', onOut, { passive: true })

    let raf = 0
    const loop = () => {
      const s = state.current
      s.rx += (s.cx - s.rx) * 0.12
      s.ry += (s.cy - s.ry) * 0.12

      dot.style.transform = `translate3d(${s.cx - 4}px, ${s.cy - 4}px, 0)`
      ring.style.transform = `translate3d(${s.rx - 20}px, ${s.ry - 20}px, 0)`
      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)

    return () => {
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseover', onOver)
      document.removeEventListener('mouseout', onOut)
      cancelAnimationFrame(raf)
    }
  }, [])

  return (
    <>
      <div
        ref={dotRef}
        className="pointer-events-none fixed left-0 top-0 z-[10000] h-2 w-2 rounded-full bg-portal-accent shadow-[0_0_20px_rgba(0,255,136,1),0_0_60px_rgba(0,255,136,0.3)]"
      />
      <div
        ref={ringRef}
        className="pointer-events-none fixed left-0 top-0 z-[10000] h-10 w-10 rounded-full border border-portal-accent/40 transition-[width,height,border-color] duration-300 [will-change:transform]"
      />
      <style>
        {`
          .is-hover {
            width: 60px !important;
            height: 60px !important;
            border-color: rgba(255,170,0,1) !important;
          }
        `}
      </style>
    </>
  )
}

