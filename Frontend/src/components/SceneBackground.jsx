import { Canvas, useFrame } from '@react-three/fiber'
import { Float } from '@react-three/drei'
import * as THREE from 'three'
import { useMemo, useRef } from 'react'

function makeRng(seed) {
  let t = seed >>> 0
  return () => {
    // mulberry32
    t += 0x6d2b79f5
    let x = Math.imul(t ^ (t >>> 15), 1 | t)
    x ^= x + Math.imul(x ^ (x >>> 7), 61 | x)
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296
  }
}

function NebulaParticles() {
  const ref = useRef()
  const { positions, colors } = useMemo(() => {
    const rand = makeRng(90210)
    const pts = 420
    const pos = new Float32Array(pts * 3)
    const col = new Float32Array(pts * 3)

    const c1 = new THREE.Color('#4FD1FF')
    const c2 = new THREE.Color('#8B5CF6')
    const c3 = new THREE.Color('#00E5FF')

    for (let i = 0; i < pts; i++) {
      const r = 7 + rand() * 10
      const theta = rand() * Math.PI * 2
      const y = (rand() - 0.5) * 7
      pos[i * 3 + 0] = Math.cos(theta) * r
      pos[i * 3 + 1] = y
      pos[i * 3 + 2] = Math.sin(theta) * r

      const t = rand()
      const c = t < 0.4 ? c1.clone().lerp(c3, rand() * 0.5) : c2.clone().lerp(c1, rand() * 0.45)
      col[i * 3 + 0] = c.r
      col[i * 3 + 1] = c.g
      col[i * 3 + 2] = c.b
    }

    return { positions: pos, colors: col }
  }, [])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    if (!ref.current) return
    ref.current.rotation.y = t * 0.03
    ref.current.rotation.x = Math.sin(t * 0.12) * 0.06
  })

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={colors.length / 3} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial size={0.06} vertexColors transparent opacity={0.42} depthWrite={false} />
    </points>
  )
}

function FloatingOrbs() {
  const group = useRef()
  const orbs = useMemo(
    () =>
      Array.from({ length: 10 }).map((_, i) => {
        const rand = makeRng(77_000 + i * 97)
        const r = 3.2 + rand() * 8
        const theta = rand() * Math.PI * 2
        const y = (rand() - 0.5) * 4.5
        const scale = 0.22 + rand() * 0.55
        const hue = i % 2 === 0 ? '#4FD1FF' : '#8B5CF6'
        return { key: i, p: [Math.cos(theta) * r, y, Math.sin(theta) * r], scale, hue }
      }),
    [],
  )

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    if (!group.current) return
    group.current.rotation.y = t * 0.045
  })

  return (
    <group ref={group}>
      {orbs.map((o) => (
        <Float key={o.key} speed={0.8} rotationIntensity={0.25} floatIntensity={0.6}>
          <mesh position={o.p} scale={o.scale}>
            <icosahedronGeometry args={[1, 1]} />
            <meshStandardMaterial color={o.hue} transparent opacity={0.18} roughness={0.35} metalness={0.2} />
          </mesh>
        </Float>
      ))}
    </group>
  )
}

export default function SceneBackground() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-0">
      <Canvas
        dpr={[1, 1.6]}
        camera={{ position: [0, 0, 12], fov: 55 }}
        gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[6, 8, 5]} intensity={0.9} color={'#b8eaff'} />
        <pointLight position={[-8, -3, 6]} intensity={0.65} color={'#9a7bff'} />
        <NebulaParticles />
        <FloatingOrbs />
      </Canvas>
      <div className="absolute inset-0 bg-gradient-to-b from-black/10 via-transparent to-black/30" />
    </div>
  )
}

