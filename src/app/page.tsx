"use client";

import React, { useState } from "react";
import axios from "axios";
import SARForm from "@/components/SARForm";
import SARReport from "@/components/SARReport";
import { 
  Sparkles, 
  Download, 
  Wand2, 
  BookOpen, 
  ArrowRight, 
  Twitter, 
  Linkedin, 
  Instagram, 
  Menu,
  X,
  Plus
} from "lucide-react";
import type { AxiosError } from "axios";

type AnalyzePayload = FormData | Record<string, unknown>;
type ApiErrorDetail = { detail?: { error?: string } };

export default function Home() {
  const [reportData, setReportData] = useState<Record<string, unknown> | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleAnalyze = async (payload: AnalyzePayload) => {
    setIsLoading(true);
    setReportData(null);
    try {
      const isCsvUpload = payload instanceof FormData;
      const response = await axios.post(
        isCsvUpload ? "http://localhost:8000/api/v1/analyze/csv" : "http://localhost:8000/api/v1/analyze",
        payload,
        isCsvUpload ? { headers: { "Content-Type": "multipart/form-data" } } : undefined
      );
      setReportData(response.data);
    } catch (error: unknown) {
      console.error("Analysis failed:", error);
      const axiosError = error as AxiosError<ApiErrorDetail>;
      alert(axiosError.response?.data?.detail?.error || axiosError.message || "Failed to analyze data");
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setReportData(null);
  };

  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);

  return (
    <main className="relative min-h-screen w-full bg-black overflow-hidden font-[family-name:var(--font-poppins)] text-white">
      {/* Background Video */}
      <video 
        autoPlay 
        loop 
        muted 
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0 opacity-80"
      >
        <source src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260315_073750_51473149-4350-4920-ae24-c8214286f323.mp4" type="video/mp4" />
      </video>

      {/* Main Content Layout */}
      <div className="relative z-10 flex flex-row min-h-screen w-full">
        
        {/* Left Panel (52%) */}
        <div className="relative w-full lg:w-[52%] h-screen p-4 lg:p-6 flex flex-col">
          <div className="liquid-glass-strong absolute inset-4 lg:inset-6 rounded-3xl -z-10"></div>
          
          {/* Nav */}
          <nav className="flex justify-between items-center w-full px-4 pt-4">
            <div className="flex items-center gap-3">
              <img 
                src="/logo.png" 
                alt="Bloom Logo" 
                className="w-8 h-8 object-contain"
                onError={(e) => { e.currentTarget.src = "https://placehold.co/32x32/222/FFF?text=B" }}
              />
              <span className="font-semibold text-2xl tracking-tighter text-white">bloom</span>
            </div>
            <button className="liquid-glass px-4 py-2 rounded-full flex items-center gap-2 hover:scale-105 transition-transform">
              <span className="text-sm font-medium">Menu</span>
              <Menu size={16} />
            </button>
          </nav>

          {/* Hero Center */}
          <div className="flex-1 flex flex-col items-center justify-center text-center px-6">
            <img 
              src="/logo.png" 
              alt="Bloom Logo Large" 
              className="w-20 h-20 object-contain mb-8"
              onError={(e) => { e.currentTarget.src = "https://placehold.co/80x80/222/FFF?text=B" }}
            />
            <h1 className="text-6xl lg:text-7xl font-medium tracking-[-0.05em] text-white leading-tight mb-10 max-w-2xl">
              Innovating the <br />
              <span className="font-[family-name:var(--font-source-serif)] italic text-white/80">spirit of bloom</span> AI
            </h1>
            
            <button 
              onClick={openModal}
              className="liquid-glass-strong px-6 py-3 rounded-full flex items-center gap-4 hover:scale-105 active:scale-95 transition-transform mb-12"
            >
              <span className="font-medium text-lg">Explore Now</span>
              <div className="w-7 h-7 rounded-full bg-white/15 flex items-center justify-center">
                <Download size={14} className="text-white" />
              </div>
            </button>

            <div className="flex flex-wrap justify-center gap-3">
              <span className="liquid-glass px-5 py-2 rounded-full text-xs text-white/80">Artistic Gallery</span>
              <span className="liquid-glass px-5 py-2 rounded-full text-xs text-white/80">AI Generation</span>
              <span className="liquid-glass px-5 py-2 rounded-full text-xs text-white/80">3D Structures</span>
            </div>
          </div>

          {/* Bottom Quote */}
          <div className="mt-auto px-6 pb-6 text-center lg:text-left">
            <div className="text-xs tracking-widest uppercase text-white/50 mb-3 font-medium">VISIONARY DESIGN</div>
            <div className="text-lg mb-3">
              "We imagined a realm <span className="font-[family-name:var(--font-source-serif)] italic text-white/80">with no ending</span>."
            </div>
            <div className="flex items-center justify-center lg:justify-start gap-3 text-xs text-white/60 uppercase tracking-widest">
              <div className="w-8 h-[1px] bg-white/30"></div>
              MARCUS AURELIO
              <div className="w-8 h-[1px] bg-white/30"></div>
            </div>
          </div>
        </div>

        {/* Right Panel (48%) - Desktop Only */}
        <div className="hidden lg:flex w-[48%] h-screen p-6 flex-col relative">
          
          {/* Top Bar */}
          <div className="flex justify-between items-center w-full mb-12">
            <div className="liquid-glass rounded-full flex items-center px-2 py-2 gap-2">
              <a href="#" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white hover:text-white/80 transition-colors">
                <Twitter size={14} />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white hover:text-white/80 transition-colors">
                <Linkedin size={14} />
              </a>
              <a href="#" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white hover:text-white/80 transition-colors">
                <Instagram size={14} />
              </a>
              <button className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white hover:text-white/80 transition-colors ml-2">
                <ArrowRight size={14} />
              </button>
            </div>

            <button className="liquid-glass px-4 py-2 rounded-full flex items-center gap-2 hover:scale-105 transition-transform">
              <Sparkles size={16} />
              <span className="text-sm font-medium">Account</span>
            </button>
          </div>

          {/* Community Card */}
          <div className="liquid-glass w-56 rounded-3xl p-5 ml-auto mr-12 hover:scale-105 transition-transform cursor-pointer">
            <h3 className="font-medium text-lg mb-2">Enter our ecosystem</h3>
            <p className="text-xs text-white/60 leading-relaxed">
              Join the community of floral architects redefining organic structures.
            </p>
          </div>

          {/* Bottom Feature Section */}
          <div className="liquid-glass mt-auto rounded-[2.5rem] p-4 flex flex-col gap-4">
            <div className="flex gap-4">
              <div className="liquid-glass flex-1 rounded-3xl p-6 hover:scale-105 transition-transform cursor-pointer">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center mb-4">
                  <Wand2 size={18} />
                </div>
                <h4 className="font-medium mb-1">Processing</h4>
                <p className="text-xs text-white/50">Neural synthesis</p>
              </div>
              <div className="liquid-glass flex-1 rounded-3xl p-6 hover:scale-105 transition-transform cursor-pointer">
                <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center mb-4">
                  <BookOpen size={18} />
                </div>
                <h4 className="font-medium mb-1">Growth Archive</h4>
                <p className="text-xs text-white/50">Stored patterns</p>
              </div>
            </div>

            <div className="liquid-glass rounded-3xl p-4 flex items-center gap-4 hover:scale-[1.02] transition-transform">
              <img 
                src="/assets/hero-flowers.png" 
                alt="Advanced Plant Sculpting" 
                className="w-24 h-16 object-cover rounded-xl"
                onError={(e) => { e.currentTarget.src = "https://placehold.co/96x64/222/FFF?text=Flowers" }}
              />
              <div className="flex-1">
                <h4 className="font-medium text-sm">Advanced Plant Sculpting</h4>
                <p className="text-xs text-white/50">Latest generation model</p>
              </div>
              <button onClick={openModal} className="liquid-glass w-10 h-10 rounded-full flex items-center justify-center hover:scale-105 transition-transform mr-2">
                <Plus size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Form / Report Modal Overlay */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 md:p-12">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/40 backdrop-blur-sm"
            onClick={closeModal}
          ></div>
          
          {/* Modal Content */}
          <div className="liquid-glass-strong w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-[2.5rem] relative z-10 flex flex-col custom-scrollbar">
            <button 
              onClick={closeModal}
              className="absolute top-6 right-6 w-10 h-10 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-colors z-20"
            >
              <X size={20} />
            </button>
            
            <div className="p-8 md:p-12">
              <div className="mb-8 text-center">
                <h2 className="text-3xl font-medium tracking-tight mb-2">SAR Intelligence</h2>
                <p className="text-sm text-white/60 font-[family-name:var(--font-source-serif)] italic">Multi-Agent Pipeline</p>
              </div>
              
              <div className="w-full flex items-center justify-center">
                {!reportData ? (
                  <SARForm onSubmit={handleAnalyze} isLoading={isLoading} />
                ) : (
                  <SARReport data={reportData} onReset={handleReset} />
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
