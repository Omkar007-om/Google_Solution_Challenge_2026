"use client";

import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, ShieldCheck, Activity, BarChart3, Clock, CheckCircle2, XCircle, ArrowLeft, FileText, Split, BookOpen } from 'lucide-react';

interface SARReportProps {
  data: Record<string, unknown>;
  onReset: () => void;
}

type TraceStep = {
  agent: string;
  status: string;
  duration_s: number;
};

type SARResult = {
  report_id?: string;
  status?: string;
  formatted_report?: string;
  risk_assessment?: {
    score?: number;
    level?: string;
    contributing_factors?: string[];
    shap_explanation?: {
      method?: string;
      top_drivers?: ShapDriver[];
    };
  };
  summary?: {
    total_amount?: number;
    total_transactions?: number;
    avg_amount?: number;
    high_value_count?: number;
  };
  review_decision?: {
    decision?: string;
    reviewer_note?: string;
  };
  rag_context?: RagSource[];
};

type ShapDriver = {
  feature: string;
  display_name: string;
  shap_value: number;
  impact_pct: number;
  reason: string;
};

type RagSource = {
  id: string;
  title: string;
  category: string;
  content: string;
};

type SARMetadata = {
  trace?: TraceStep[];
  total_duration_s?: number;
  cached?: boolean;
};

export default function SARReport({ data, onReset }: SARReportProps) {
  const result = (data.result || {}) as SARResult;
  const metadata = (data.metadata || {}) as SARMetadata;
  const risk = result.risk_assessment || {};
  const summary = result.summary || {};
  const trace = metadata.trace || [];
  const review = result.review_decision || {};
  const shapDrivers = risk.shap_explanation?.top_drivers || [];
  const ragContext = result.rag_context || [];

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
                
                {trace.map((step, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.3 + (idx * 0.1) }}
                    className="relative flex flex-col items-center group flex-1 min-w-24"
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

        {shapDrivers.length > 0 && (
          <motion.div variants={itemVariants} className="glass-panel p-6 rounded-2xl md:col-span-3">
            <div className="flex items-center gap-2 mb-5 text-brand-accent">
              <Split size={20} />
              <h3 className="font-semibold text-white">SHAP Explainability</h3>
            </div>
            <div className="space-y-3">
              {shapDrivers.map((driver) => (
                <div key={driver.feature} className="grid gap-2 rounded-lg border border-white/10 bg-black/30 p-4 md:grid-cols-[220px_1fr_90px] md:items-center">
                  <div>
                    <div className="text-sm font-semibold text-white">{driver.display_name}</div>
                    <div className="text-xs text-gray-500">+{driver.shap_value} risk points</div>
                  </div>
                  <div className="h-2 rounded-full bg-white/10">
                    <div
                      className="h-2 rounded-full bg-brand-accent"
                      style={{ width: `${Math.min(driver.impact_pct, 100)}%` }}
                    />
                  </div>
                  <div className="text-right text-sm font-bold text-white">{driver.impact_pct}%</div>
                  <p className="text-sm text-gray-400 md:col-span-3">{driver.reason}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {ragContext.length > 0 && (
          <motion.div variants={itemVariants} className="glass-panel p-6 rounded-2xl md:col-span-3">
            <div className="flex items-center gap-2 mb-5 text-brand-accent">
              <BookOpen size={20} />
              <h3 className="font-semibold text-white">RAG Knowledge Retrieved</h3>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              {ragContext.map((source) => (
                <div key={source.id} className="rounded-lg border border-white/10 bg-black/30 p-4">
                  <div className="text-xs text-gray-500">{source.category} | {source.id}</div>
                  <div className="mt-1 text-sm font-semibold text-white">{source.title}</div>
                  <p className="mt-2 text-sm leading-6 text-gray-400">{source.content}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        <motion.div variants={itemVariants} className="glass-panel p-6 rounded-2xl md:col-span-3">
          <div className="flex items-center justify-between gap-4 mb-5">
            <div className="flex items-center gap-2 text-brand-accent">
              <FileText size={20} />
              <h3 className="font-semibold text-white">Humanised SAR Report</h3>
            </div>
            <div className="text-xs text-gray-300 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5">
              {review.decision || result.status}
            </div>
          </div>
          <pre className="whitespace-pre-wrap rounded-xl border border-white/10 bg-black/40 p-5 text-sm leading-6 text-gray-200 overflow-x-auto">
            {result.formatted_report}
          </pre>
          {review.reviewer_note && (
            <p className="mt-4 text-sm text-gray-400">{review.reviewer_note}</p>
          )}
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
