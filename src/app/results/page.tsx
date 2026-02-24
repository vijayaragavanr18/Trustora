"use client";

import { Navbar } from "@/components/Navbar";
import { AlertTriangle, CheckCircle, Download, FileText, Share2, ShieldAlert } from "lucide-react";
import { motion } from "framer-motion";

export default function AnalysisResults() {
  // Mock data for the demonstration
  const analysisData = {
    id: "TR-2024-8X92",
    timestamp: new Date().toLocaleString(),
    filename: "suspect_video_clip.mp4",
    score: 94.2,
    riskLevel: "High",
    confidence: "Very High",
    details: [
      { name: "Face Morfing Artifacts", status: "Detected", risk: "High" },
      { name: "Inconsistent Noise Patterns", status: "Detected", risk: "Medium" },
      { name: "Audio-Visual Sync", status: "Normal", risk: "Low" },
      { name: "Metadata Analysis", status: "Suspicious", risk: "Medium" },
    ],
  };

  const riskColor = analysisData.score > 70 ? "text-red-500" : analysisData.score > 40 ? "text-yellow-500" : "text-green-500";
  const riskBg = analysisData.score > 70 ? "bg-red-500/10 border-red-500/20" : analysisData.score > 40 ? "bg-yellow-500/10 border-yellow-500/20" : "bg-green-500/10 border-green-500/20";

  return (
    <div className="min-h-screen bg-background bg-grid bg-radial-fade">
      <Navbar />
      <main className="container mx-auto px-6 py-8 max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-8"
        >
          {/* Left Column: Visuals */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-card border border-border rounded-xl overflow-hidden shadow-lg relative group">
              <div className="absolute top-4 left-4 z-10 bg-black/60 backdrop-blur-md px-3 py-1 rounded-full text-xs font-mono border border-white/10">
                FRAME ANALYZED: 00:04:12
              </div>
              <div className="relative aspect-video bg-black/50 flex items-center justify-center overflow-hidden">
                {/* Simulated Heatmap Overlay */}
                <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-red-500/20 to-transparent opacity-60 mix-blend-overlay" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-red-500/30 blur-3xl rounded-full" />
                
                <span className="text-muted-foreground font-mono text-sm opacity-50">
                  [ Video Frame Preview ]
                </span>
                
                {/* Bounding Box Simulation */}
                <div className="absolute top-[30%] left-[40%] w-[20%] h-[40%] border-2 border-red-500/70 rounded-lg shadow-[0_0_15px_rgba(239,68,68,0.5)]">
                    <div className="absolute -top-6 left-0 bg-red-500 text-white text-[10px] px-2 py-0.5 rounded-t">
                        CONFIDENCE: 98%
                    </div>
                </div>
              </div>
              
              <div className="p-4 bg-card/50 border-t border-border flex justify-between items-center text-sm">
                 <div className="flex gap-4">
                    <span className="text-muted-foreground">Frame 249/1800</span>
                    <span className="text-muted-foreground">1080p HEVC</span>
                 </div>
                 <button className="text-primary hover:text-primary/80 transition-colors font-medium">
                    View Frame by Frame
                 </button>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {analysisData.details.map((item, i) => (
                    <motion.div 
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.2 + (i * 0.1) }}
                        key={item.name} 
                        className="bg-card border border-border p-4 rounded-xl hover:border-primary/30 transition-colors"
                    >
                        <div className="flex justify-between items-start mb-2">
                            <span className="font-medium text-foreground">{item.name}</span>
                            <span className={`text-xs px-2 py-0.5 rounded-full border ${
                                item.risk === "High" ? "bg-red-500/10 border-red-500/20 text-red-500" :
                                item.risk === "Medium" ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-500" :
                                "bg-green-500/10 border-green-500/20 text-green-500"
                            }`}>
                                {item.risk}
                            </span>
                        </div>
                        <p className="text-sm text-muted-foreground">{item.status}</p>
                    </motion.div>
                ))}
            </div>
          </div>

          {/* Right Column: Report Summary */}
          <div className="space-y-6">
            <div className={`p-6 rounded-2xl border ${riskBg} flex flex-col items-center text-center relative overflow-hidden`}>
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <ShieldAlert className="w-32 h-32" />
                </div>
                
                <h2 className="text-sm font-semibold uppercase tracking-widest mb-1 opacity-80">Deepfake Probability</h2>
                <div className={`text-6xl font-display font-bold mb-2 ${riskColor}`}>
                    {analysisData.score}%
                </div>
                <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium border ${riskBg} ${riskColor}`}>
                    <AlertTriangle className="w-4 h-4" />
                    {analysisData.riskLevel} Risk Detected
                </div>
            </div>

            <div className="bg-card border border-border rounded-xl p-6 shadow-sm">
                <h3 className="font-semibold text-lg mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-primary" />
                    Report Details
                </h3>
                
                <div className="space-y-4 text-sm">
                    <div className="flex justify-between py-2 border-b border-border/50">
                        <span className="text-muted-foreground">Analysis ID</span>
                        <span className="font-mono">{analysisData.id}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-border/50">
                        <span className="text-muted-foreground">Timestamp</span>
                        <span>{analysisData.timestamp}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-border/50">
                        <span className="text-muted-foreground">File Name</span>
                        <span className="truncate max-w-[150px]">{analysisData.filename}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b border-border/50">
                        <span className="text-muted-foreground">Model Version</span>
                        <span>v2.4.1 (Ensemble)</span>
                    </div>
                </div>

                <div className="mt-6 space-y-3">
                    <button className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground py-2.5 rounded-lg active:scale-95 transition-transform hover:opacity-90 font-medium">
                        <Download className="w-4 h-4" />
                        Download Full Report (PDF)
                    </button>
                    <button className="w-full flex items-center justify-center gap-2 bg-secondary text-secondary-foreground border border-border py-2.5 rounded-lg hover:bg-secondary/80 transition-colors font-medium">
                        <Share2 className="w-4 h-4" />
                        Share Analysis
                    </button>
                </div>
            </div>

            <div className="bg-primary/5 border border-primary/10 rounded-xl p-4">
                <h4 className="font-medium text-sm text-primary mb-2 flex items-center gap-2">
                    <CheckCircle className="w-4 h-4" />
                    Recommended Actions
                </h4>
                <ul className="text-sm text-muted-foreground space-y-2 list-disc pl-4">
                    <li>Flag content for manual review</li>
                    <li>Do not verify as authentic evidence</li>
                    <li>Check metadata for origin trace</li>
                </ul>
            </div>
          </div>
        </motion.div>
      </main>
    </div>
  );
}
