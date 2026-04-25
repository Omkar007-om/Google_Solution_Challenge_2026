"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, ShieldCheck, Activity, BarChart3, Clock, CheckCircle2, XCircle, ArrowLeft } from 'lucide-react';

interface SARReportProps {
  data: any;
  onReset: () => void;
}

export default function SARReport({ data, onReset }: SARReportProps) {
  const result = data.result || {};
  const metadata = data.metadata || {};
  const risk = result.risk_assessment || {};
  const summary = result.summary || {};
  const trace = metadata.trace || [];

  const isHighRisk = risk.score >= 60;
  const RiskIcon = isHighRisk ? ShieldAlert : ShieldCheck;
  const riskColor = isHighRisk 
    ? 'text-rose-500 from-rose-500/20 to-rose-500/0 border-rose-500/30' 
    : 'text-emerald-500 from-emerald-500/20 to-emerald-500/0 border-emerald-500/30';

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-white tracking-tight">Analysis Complete</h2>
          <p className="text-gray-400 font-mono text-sm mt-2">Report ID: {result.report_id}</p>
        </div>
        <button 
          onClick={onReset}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-300 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 transition-colors"
        >
          <ArrowLeft size={16} />
          New Analysis
        </button>
      </div>

      <motion.div variants={containerVariants} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Risk Score Card */}
        <motion.div variants={itemVariants} className={`glass-panel p-6 rounded-2xl flex flex-col items-center justify-center text-center bg-gradient-to-b ${riskColor} relative overflow-hidden`}>
          <RiskIcon size={48} className="mb-4 drop-shadow-lg" />
          <h3 className="text-gray-300 text-sm font-medium uppercase tracking-wider mb-1">Risk Assessment</h3>
          <div className="text-5xl font-black text-white mb-2">{risk.score}<span className="text-xl text-white/50">/100</span></div>
          <div className="inline-flex items-center px-3 py-1 rounded-full bg-black/30 border border-white/10 text-sm font-bold tracking-widest">
            {risk.level}
          </div>
        </motion.div>

        {/* Financial Summary */}
        <motion.div variants={itemVariants} className="glass-panel p-6 rounded-2xl md:col-span-2">
          <div className="flex items-center gap-2 mb-6 text-brand-accent">
            <BarChart3 size={20} />
            <h3 className="font-semibold text-white">Transaction Summary</h3>
          </div>
          
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <StatBox label="Total Volume" value={`$${summary.total_amount?.toLocaleString()}`} />
            <StatBox label="Count" value={summary.total_transactions} />
            <StatBox label="Average" value={`$${summary.avg_amount?.toLocaleString()}`} />
            <StatBox label="High Value (>10k)" value={summary.high_value_count} highlight />
          </div>

          {risk.contributing_factors?.length > 0 && (
            <div className="mt-6 pt-6 border-t border-white/10">
              <h4 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">Contributing Factors</h4>
              <ul className="space-y-2">
                {risk.contributing_factors.map((factor: string, i: number) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-300 bg-white/5 p-2 rounded-lg border border-white/5">
                    <Activity size={16} className="text-rose-400 shrink-0 mt-0.5" />
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </motion.div>

        {/* Pipeline Execution Trace */}
        <motion.div variants={itemVariants} className="glass-panel p-6 rounded-2xl md:col-span-3">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2 text-brand-secondary">
              <Activity size={20} />
              <h3 className="font-semibold text-white">Agent Pipeline Execution Trace</h3>
            </div>
            <div className="text-xs text-gray-400 font-mono flex items-center gap-1.5 bg-black/40 px-3 py-1.5 rounded-lg border border-white/5">
              <Clock size={14} />
              {metadata.total_duration_s}s total {metadata.cached && <span className="text-brand-accent ml-2">(Served from Cache)</span>}
            </div>
          </div>

          <div className="overflow-x-auto">
            <div className="min-w-[600px]">
              <div className="flex items-center justify-between relative">
                {/* Connecting Line */}
                <div className="absolute top-1/2 left-0 w-full h-0.5 bg-white/10 -z-10 -translate-y-1/2"></div>
                
                {trace.map((step: any, idx: number) => (
                  <motion.div 
                    key={idx}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.3 + (idx * 0.1) }}
                    className="relative flex flex-col items-center group w-1/5"
                  >
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center border-2 mb-3 bg-black transition-transform group-hover:scale-110 ${step.status === 'success' ? 'border-brand-primary text-brand-primary shadow-[0_0_15px_rgba(99,102,241,0.5)]' : 'border-rose-500 text-rose-500'}`}>
                      {step.status === 'success' ? <CheckCircle2 size={20} /> : <XCircle size={20} />}
                    </div>
                    <div className="text-xs font-bold text-white mb-1">{step.agent}</div>
                    <div className="text-[10px] text-gray-400 font-mono bg-white/5 px-2 py-0.5 rounded border border-white/5">{step.duration_s}s</div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.div>

      </motion.div>
    </div>
  );
}

function StatBox({ label, value, highlight = false }: { label: string; value: string | number; highlight?: boolean }) {
  return (
    <div className={`bg-black/40 border border-white/5 rounded-xl p-4 ${highlight ? 'ring-1 ring-brand-accent/30 bg-brand-accent/5' : ''}`}>
      <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">{label}</div>
      <div className={`text-xl font-bold ${highlight ? 'text-brand-accent text-glow' : 'text-white'}`}>{value}</div>
    </div>
  );
}
