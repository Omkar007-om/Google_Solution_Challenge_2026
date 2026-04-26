"use client";

import React, { useState } from "react";
import { AlertCircle, FileJson, FileUp, Play } from "lucide-react";
import { motion } from "framer-motion";

interface SARFormProps {
  onSubmit: (payload: FormData | Record<string, unknown>) => void;
  isLoading: boolean;
}

const DEFAULT_PAYLOAD = {
  input_data: {
    user_id: "ACC999",
    transactions: [
      { id: "TXN004", time: "2024-03-12 14:00", amt: "49000", from_acc: "ACC999", to_acc: "ACC300", location: "Mumbai" },
      { id: "TXN005", time: "2024-03-12 14:05", amt: "49500", from_acc: "ACC999", to_acc: "ACC301", location: "Mumbai" },
      { id: "TXN006", time: "2024-03-12 14:10", amt: "48700", from_acc: "ACC999", to_acc: "ACC302", location: "Mumbai" },
      { id: "TXN007", time: "2024-03-12 15:00", amt: "2500000", from_acc: "ACC400", to_acc: "ACC999", location: "Dubai", note: "consulting" },
      { id: "TXN008", time: "2024-03-12 15:10", amt: "2450000", from_acc: "ACC999", to_acc: "ACC888", location: "Cayman Islands" }
    ]
  }
};

export default function SARForm({ onSubmit, isLoading }: SARFormProps) {
  const [mode, setMode] = useState<"csv" | "json">("csv");
  const [jsonText, setJsonText] = useState(JSON.stringify(DEFAULT_PAYLOAD, null, 2));
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [subjectAccount, setSubjectAccount] = useState("ACC999");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    if (mode === "csv") {
      if (!csvFile) {
        setError("Select a CSV file first.");
        return;
      }
      const formData = new FormData();
      formData.append("file", csvFile);
      if (subjectAccount.trim()) {
        formData.append("subject_account", subjectAccount.trim());
      }
      onSubmit(formData);
      return;
    }

    try {
      const parsed = JSON.parse(jsonText);
      if (!parsed.input_data) {
        throw new Error("Payload must contain input_data at the root.");
      }
      onSubmit(parsed);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Invalid JSON payload");
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-xl p-6 sm:p-8 w-full max-w-4xl mx-auto"
    >
      <div className="flex items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-brand-primary/20 rounded-lg text-brand-primary">
            {mode === "csv" ? <FileUp size={24} /> : <FileJson size={24} />}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">SAR Intake</h2>
            <p className="text-gray-400 text-sm mt-1">Run the seven-agent pipeline from CSV or JSON</p>
          </div>
        </div>

        <div className="flex rounded-lg border border-white/10 bg-black/30 p-1">
          <button
            type="button"
            onClick={() => setMode("csv")}
            className={`px-3 py-1.5 text-sm rounded-md ${mode === "csv" ? "bg-white/10 text-white" : "text-gray-400"}`}
          >
            CSV
          </button>
          <button
            type="button"
            onClick={() => setMode("json")}
            className={`px-3 py-1.5 text-sm rounded-md ${mode === "json" ? "bg-white/10 text-white" : "text-gray-400"}`}
          >
            JSON
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {mode === "csv" ? (
          <div className="space-y-4">
            <label className="block">
              <span className="text-sm font-medium text-gray-300">Subject account</span>
              <input
                value={subjectAccount}
                onChange={(event) => setSubjectAccount(event.target.value)}
                className="mt-2 w-full rounded-lg border border-white/10 bg-black/40 px-4 py-3 text-white outline-none focus:border-brand-accent"
                placeholder="ACC999"
              />
            </label>

            <label className="flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-white/20 bg-black/30 p-6 text-center transition hover:border-brand-accent/70 hover:bg-white/5">
              <FileUp className="mb-3 text-brand-accent" size={34} />
              <span className="text-white font-semibold">{csvFile ? csvFile.name : "Choose CSV file"}</span>
              <span className="mt-2 text-sm text-gray-400">Accepted columns include id, time, amount/amt, from_acc, to_acc, location, note</span>
              <input
                type="file"
                accept=".csv,text/csv"
                className="hidden"
                onChange={(event) => setCsvFile(event.target.files?.[0] || null)}
              />
            </label>
          </div>
        ) : (
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
              onChange={(event) => setJsonText(event.target.value)}
              className="w-full h-80 bg-transparent text-gray-300 font-mono text-sm p-4 focus:outline-none resize-none"
              spellCheck={false}
            />
          </div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
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
            className="inline-flex items-center gap-2 px-7 py-3 font-semibold text-white transition rounded-lg bg-brand-primary hover:bg-brand-secondary active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
          >
            {isLoading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Processing
              </>
            ) : (
              <>
                Run Analysis
                <Play size={18} />
              </>
            )}
          </button>
        </div>
      </form>
    </motion.div>
  );
}
