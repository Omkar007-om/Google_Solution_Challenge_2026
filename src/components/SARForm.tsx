"use client";

import React, { useState } from 'react';
import { Play, FileJson, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface SARFormProps {
  onSubmit: (payload: any) => void;
  isLoading: boolean;
}

const DEFAULT_PAYLOAD = {
  input_data: {
    user_id: "USR-042",
    transactions: [
      { amount: 15000, type: "wire", timestamp: "2026-04-25T10:00:00Z" },
      { amount: 3200, type: "deposit", timestamp: "2026-04-25T11:30:00Z" },
      { amount: 52000, type: "wire", timestamp: "2026-04-25T14:00:00Z" },
      { amount: 8700, type: "ach", timestamp: "2026-04-25T15:45:00Z" },
      { amount: 25000, type: "wire", timestamp: "2026-04-25T16:00:00Z" }
    ]
  }
};

export default function SARForm({ onSubmit, isLoading }: SARFormProps) {
  const [jsonText, setJsonText] = useState(JSON.stringify(DEFAULT_PAYLOAD, null, 2));
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      const parsed = JSON.parse(jsonText);
      if (!parsed.input_data) {
         throw new Error("Payload must contain 'input_data' at the root.");
      }
      onSubmit(parsed);
    } catch (err: any) {
      setError(err.message || "Invalid JSON payload");
    }
  };

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-2xl p-6 sm:p-8 w-full max-w-4xl mx-auto"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2.5 bg-brand-primary/20 rounded-lg text-brand-primary">
          <FileJson size={24} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight">Data Ingestion</h2>
          <p className="text-gray-400 text-sm mt-1">Submit raw transaction payloads to the SAR pipeline</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-brand-primary to-brand-secondary rounded-xl opacity-20 group-focus-within:opacity-50 blur transition duration-500"></div>
          <div className="relative bg-black/50 rounded-xl overflow-hidden border border-white/10 focus-within:border-brand-primary/50 transition-colors">
            <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/5">
              <span className="text-xs font-mono text-gray-400">payload.json</span>
              <button 
                type="button"
                onClick={() => setJsonText(JSON.stringify(DEFAULT_PAYLOAD, null, 2))}
                className="text-xs text-brand-accent hover:text-white transition-colors"
              >
                Reset Default
              </button>
            </div>
            <textarea
              value={jsonText}
              onChange={(e) => setJsonText(e.target.value)}
              className="w-full h-80 bg-transparent text-gray-300 font-mono text-sm p-4 focus:outline-none resize-none"
              spellCheck={false}
            />
          </div>
        </div>

        {error && (
          <motion.div 
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="flex items-center gap-2 text-red-400 bg-red-400/10 p-3 rounded-lg text-sm border border-red-400/20"
          >
            <AlertCircle size={16} />
            <span>{error}</span>
          </motion.div>
        )}

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isLoading}
            className="group relative inline-flex items-center gap-2 px-8 py-3.5 font-semibold text-white transition-all duration-300 rounded-xl hover:scale-105 active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
          >
            <span className="absolute inset-0 w-full h-full rounded-xl bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-primary bg-[length:200%_auto] animate-[gradient_3s_linear_infinite] opacity-80 group-hover:opacity-100 blur-sm transition-opacity"></span>
            <span className="absolute inset-0 w-full h-full rounded-xl bg-gradient-to-r from-brand-primary to-brand-secondary"></span>
            <span className="relative flex items-center gap-2">
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  Run Analysis
                  <Play size={18} className="transition-transform group-hover:translate-x-1" />
                </>
              )}
            </span>
          </button>
        </div>
      </form>
    </motion.div>
  );
}
