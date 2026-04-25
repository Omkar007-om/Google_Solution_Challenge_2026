"use client";

import React, { useState } from "react";
import axios from "axios";
import SARForm from "@/components/SARForm";
import SARReport from "@/components/SARReport";
import { ShieldAlert } from "lucide-react";

export default function Home() {
  const [reportData, setReportData] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyze = async (payload: any) => {
    setIsLoading(true);
    setReportData(null);
    try {
      // Connect to the SAR Multi-Agent Backend running on port 8000
      const response = await axios.post("http://localhost:8000/api/v1/analyze", payload);
      setReportData(response.data);
    } catch (error: any) {
      console.error("Analysis failed:", error);
      alert(error.response?.data?.detail?.error || error.message || "Failed to analyze data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setReportData(null);
  };

  return (
    <main className="min-h-screen p-6 md:p-12 relative flex flex-col items-center">
      {/* Premium Header */}
      <header className="w-full max-w-6xl mx-auto flex items-center justify-between mb-12">
        <div className="flex items-center gap-3">
          <div className="bg-brand-primary p-2 rounded-lg text-white shadow-[0_0_15px_rgba(99,102,241,0.5)]">
            <ShieldAlert size={28} />
          </div>
          <div>
            <h1 className="text-xl md:text-2xl font-bold tracking-tight text-white">SAR Intelligence</h1>
            <p className="text-brand-accent text-xs font-mono tracking-widest uppercase mt-0.5 text-glow">Multi-Agent Pipeline</p>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-4 text-sm font-medium text-gray-400">
          <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>Backend Connected</span>
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 w-full flex items-center justify-center">
        {!reportData ? (
          <SARForm onSubmit={handleAnalyze} isLoading={isLoading} />
        ) : (
          <SARReport data={reportData} onReset={handleReset} />
        )}
      </div>
    </main>
  );
}
