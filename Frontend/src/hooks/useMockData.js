import { useEffect, useMemo, useState } from 'react'

const LOCATIONS = [
  'Mumbai, IN',
  'Dubai, AE',
  'Singapore, SG',
  'London, UK',
  'New York, US',
  'Frankfurt, DE',
  'Hong Kong, HK',
  'Toronto, CA',
  'Zurich, CH',
  'Tokyo, JP',
]

const MERCHANTS = [
  'NEX-OTC Desk',
  'Orion Digital',
  'Helios Exchange',
  'Atlas Remit',
  'Nova Pay',
  'Kestrel Labs',
  'Aster Bank',
  'Nightfall Markets',
]

function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n))
}

function rnd(seedRef) {
  // simple deterministic-ish rng (mulberry32-like)
  let t = (seedRef.current += 0x6d2b79f5)
  t = Math.imul(t ^ (t >>> 15), t | 1)
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296
}

function pick(seedRef, arr) {
  return arr[Math.floor(rnd(seedRef) * arr.length)]
}

function fmtMoney(n) {
  return n.toLocaleString(undefined, { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
}

function isoTimeAgo(msAgo) {
  const d = new Date(Date.now() - msAgo)
  return d.toISOString().slice(0, 19).replace('T', ' ')
}

export function useMockData({ count = 48, suspiciousThreshold = 72 } = {}) {
  const [baseSeed] = useState(() => 1337)
  const [tick, setTick] = useState(0)

  useEffect(() => {
    const id = window.setInterval(() => setTick((t) => t + 1), 4000)
    return () => window.clearInterval(id)
  }, [])

  const data = useMemo(() => {
    const seed = { current: baseSeed + tick * 97 }

    const transactions = Array.from({ length: count }).map((_, i) => {
      const base = rnd(seed)
      const amount = Math.round((base ** 2) * 250000 + rnd(seed) * 9000)
      const riskRaw =
        (rnd(seed) * 55 +
          (amount > 90000 ? 18 : 0) +
          (rnd(seed) > 0.88 ? 28 : 0) +
          (rnd(seed) > 0.94 ? 22 : 0)) *
        1.05
      const risk = clamp(Math.round(riskRaw), 2, 99)

      const flagged = risk >= suspiciousThreshold || (amount > 140000 && rnd(seed) > 0.55)
      const id = `TX-${String(100000 + i + tick * 7).slice(-6)}`

      const location = pick(seed, LOCATIONS)
      const merchant = pick(seed, MERCHANTS)
      const time = isoTimeAgo((i * 7 + Math.floor(rnd(seed) * 18)) * 60 * 1000)

      return {
        id,
        amount,
        amountLabel: fmtMoney(amount),
        location,
        merchant,
        time,
        risk,
        flagged,
      }
    })

    const suspicious = transactions.filter((t) => t.flagged)
    const avgRisk = Math.round(
      transactions.reduce((acc, t) => acc + t.risk, 0) / Math.max(1, transactions.length),
    )

    const riskScore = clamp(Math.round(avgRisk + suspicious.length * 0.6), 1, 99)

    const activity = [
      { kind: 'model', msg: 'Streaming telemetry: payment rails + device signals', t: isoTimeAgo(55 * 1000) },
      { kind: 'system', msg: 'Ruleset v3.8 engaged (velocity, geo, structuring)', t: isoTimeAgo(2 * 60 * 1000) },
      { kind: 'alert', msg: 'Unusual corridor detected: AE → IN (high amount)', t: isoTimeAgo(5 * 60 * 1000) },
      { kind: 'model', msg: 'Graph link score increased for shared beneficiary cluster', t: isoTimeAgo(9 * 60 * 1000) },
      { kind: 'system', msg: 'SAR drafting engine warmed (context window 30 days)', t: isoTimeAgo(12 * 60 * 1000) },
      { kind: 'alert', msg: 'Potential structuring: 6 tx under threshold within 2h', t: isoTimeAgo(17 * 60 * 1000) },
    ]

    const top = suspicious
      .slice()
      .sort((a, b) => b.risk - a.risk)
      .slice(0, 4)

    const sar = {
      summary: `We observed a concentration of ${suspicious.length} suspicious transactions across multiple jurisdictions with elevated risk signals (geo-velocity, beneficiary clustering, and threshold-adjacent structuring). The session risk score is ${riskScore}/100 with several high-severity outliers.`,
      keyFindings: [
        `Highest-risk event: ${top[0]?.id ?? 'N/A'} at ${top[0]?.amountLabel ?? '—'} from ${top[0]?.location ?? '—'} (risk ${top[0]?.risk ?? '—'}).`,
        `${Math.max(2, Math.round(suspicious.length * 0.55))} flagged events show corridor anomalies (unexpected origin/destination patterns).`,
        `Velocity spike: bursts of payments within short windows suggest possible layering attempts.`,
        `Entity linkage: repeated merchants/beneficiaries indicate coordinated activity across accounts.`,
      ],
      riskExplanation: `Risk scoring blends behavioral features (velocity, amount deviation, corridor novelty), rule triggers (threshold proximity, rapid retries), and model evidence (graph linkage, device fingerprint divergence). This batch trends toward high risk due to elevated outliers, clustering, and repeated near-threshold amounts.`,
    }

    return {
      suspiciousThreshold,
      transactions,
      totals: {
        totalTransactions: transactions.length,
        suspiciousTransactions: suspicious.length,
        riskScore,
      },
      activity,
      sar,
    }
  }, [baseSeed, count, suspiciousThreshold, tick])

  return data
}

