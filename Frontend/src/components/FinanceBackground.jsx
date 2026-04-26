import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Stars, Float, Sparkles } from '@react-three/drei'
import * as THREE from 'three'

function NetworkGlobe() {
  const groupRef = useRef()

  // Generate random points on a sphere for the data nodes with vibrant colors
  const [positions, lines, pointColors, lineColors] = useMemo(() => {
    const pts = []
    const pColors = []
    const radius = 2.5
    
    // Vibrant, attractive color palette
    const palette = [
      new THREE.Color('#FF2A6D'), // Bright Pink
      new THREE.Color('#05D9E8'), // Neon Cyan
      new THREE.Color('#FFC300'), // Vibrant Yellow
      new THREE.Color('#7000FF')  // Deep Purple
    ]

    for (let i = 0; i < 400; i++) {
      const u = Math.random()
      const v = Math.random()
      const theta = 2 * Math.PI * u
      const phi = Math.acos(2 * v - 1)
      const x = radius * Math.sin(phi) * Math.cos(theta)
      const y = radius * Math.sin(phi) * Math.sin(theta)
      const z = radius * Math.cos(phi)
      pts.push(new THREE.Vector3(x, y, z))
      
      const randomColor = palette[Math.floor(Math.random() * palette.length)]
      pColors.push(randomColor.r, randomColor.g, randomColor.b)
    }
    
    // Create random connection lines between close points
    const lns = []
    const lColors = []
    for (let i = 0; i < pts.length; i++) {
      for (let j = i + 1; j < pts.length; j++) {
        if (pts[i].distanceTo(pts[j]) < 0.8) {
          lns.push(pts[i], pts[j])
          
          // Line color blends the colors of the two connected points
          // To keep it simple, we just use the color of the first point for both vertices of the line segment
          const c1Idx = i * 3
          const c2Idx = j * 3
          lColors.push(
            pColors[c1Idx], pColors[c1Idx+1], pColors[c1Idx+2],
            pColors[c2Idx], pColors[c2Idx+1], pColors[c2Idx+2]
          )
        }
      }
    }
    
    const positionsArray = new Float32Array(pts.length * 3)
    pts.forEach((p, i) => {
      positionsArray[i * 3] = p.x
      positionsArray[i * 3 + 1] = p.y
      positionsArray[i * 3 + 2] = p.z
    })

    return [
      positionsArray, 
      lns, 
      new Float32Array(pColors), 
      new Float32Array(lColors)
    ]
  }, [])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.05
      groupRef.current.rotation.z = t * 0.02
    }
  })

  return (
    <group ref={groupRef}>
      {/* Glowing Core Sphere */}
      <mesh>
        <icosahedronGeometry args={[2.3, 3]} />
        <meshBasicMaterial color="#111122" transparent opacity={0.6} />
      </mesh>

      {/* Wireframe Globe */}
      <mesh>
        <icosahedronGeometry args={[2.4, 2]} />
        <meshBasicMaterial color="#05D9E8" wireframe transparent opacity={0.1} />
      </mesh>

      {/* Connection Lines (Colorful) */}
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={lines.length}
            array={new Float32Array(lines.flatMap(v => [v.x, v.y, v.z]))}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-color"
            count={lineColors.length / 3}
            array={lineColors}
            itemSize={3}
          />
        </bufferGeometry>
        <lineBasicMaterial vertexColors transparent opacity={0.3} />
      </lineSegments>

      {/* Data Nodes (Colorful) */}
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            count={positions.length / 3}
            array={positions}
            itemSize={3}
          />
          <bufferAttribute
            attach="attributes-color"
            count={pointColors.length / 3}
            array={pointColors}
            itemSize={3}
          />
        </bufferGeometry>
        <pointsMaterial size={0.06} vertexColors transparent opacity={1} sizeAttenuation />
      </points>
    </group>
  )
}

function DataRings() {
  const ring1 = useRef()
  const ring2 = useRef()
  const ring3 = useRef()

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    if (ring1.current) ring1.current.rotation.x = t * 0.1
    if (ring2.current) ring2.current.rotation.y = t * -0.15
    if (ring3.current) ring3.current.rotation.z = t * 0.08
  })

  return (
    <group>
      <mesh ref={ring1} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[3.2, 0.015, 16, 100]} />
        <meshBasicMaterial color="#FF2A6D" transparent opacity={0.5} />
      </mesh>
      <mesh ref={ring2} rotation={[0, Math.PI / 4, 0]}>
        <torusGeometry args={[3.8, 0.025, 16, 100]} />
        <meshBasicMaterial color="#05D9E8" transparent opacity={0.6} />
      </mesh>
      <mesh ref={ring3} rotation={[0, 0, Math.PI / 3]}>
        <torusGeometry args={[4.5, 0.015, 16, 100]} />
        <meshBasicMaterial color="#FFC300" transparent opacity={0.4} />
      </mesh>
    </group>
  )
}

export default function FinanceBackground() {
  return (
    <div className="absolute inset-0 w-full h-full -z-10 bg-[#0b0c10]">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        {/* Colorful deep space background */}
        <Stars radius={100} depth={50} count={3000} factor={4} saturation={1} fade speed={1} color="#ffffff" />
        
        {/* Floating background particles */}
        <Sparkles count={300} scale={15} size={2} speed={0.4} opacity={0.3} color="#05D9E8" />
        <Sparkles count={200} scale={15} size={1.5} speed={0.3} opacity={0.2} color="#FF2A6D" />

        <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
          <NetworkGlobe />
          <DataRings />
        </Float>
      </Canvas>
    </div>
  )
}
