'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { api } from '@/lib/api';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AnalysisPage() {
  const params = useParams();
  const router = useRouter();
  const scanId = params.id as string;

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('processing');
  const [activeStep, setActiveStep] = useState(0);


  const steps = [
    { id: 'cnn', name: 'Signal Artifact Detection', icon: '🖼️' },
    { id: 'temporal', name: 'Temporal Frame Analysis', icon: '⏰' },
    { id: 'ai', name: 'AI Deepfake Model Inference', icon: '🤖' },
    { id: 'cross', name: 'Ensemble Score Calculation', icon: '⚖️' },
  ];

  useEffect(() => {
    let isMounted = true;
    let pollInterval: NodeJS.Timeout;

    const stepInterval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % steps.length);
    }, 3000);

    const checkStatus = async () => {
      try {
        if (!api.isAuthenticated()) { router.push('/login'); return true; }
        const statusData = await api.getAnalysisStatus(scanId);
        if (isMounted) setStatus(statusData.status);

        if (statusData.status === 'completed') {
          const data = await api.getResult(scanId);
          if (isMounted) setResult(data);
          return true;
        } else if (statusData.status === 'failed') {
          throw new Error('Analysis failed. Please try a different file.');
        } else if (statusData.status === 'pending') {
          try { await api.startAnalysis(scanId); } catch (_) {}
          return false;
        }
        return false;
      } catch (err: any) {
        if (isMounted) setError(err.response?.data?.detail || err.message || 'Failed to analyze');
        return true;
      }
    };

    const startPolling = async () => {
      const finished = await checkStatus();
      if (!finished && isMounted) {
        setLoading(true);
        pollInterval = setInterval(async () => {
          const done = await checkStatus();
          if (done && isMounted) {
            clearInterval(pollInterval);
            clearInterval(stepInterval);
            setLoading(false);
          }
        }, 2000);
      } else {
        if (isMounted) { clearInterval(stepInterval); setLoading(false); }
      }
    };

    if (scanId) startPolling();
    return () => {
      isMounted = false;
      if (pollInterval) clearInterval(pollInterval);
      clearInterval(stepInterval);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scanId]);



  // ── LOADING STATE ─────────────────────────────────────────────────────────
  if (loading) return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
      <div
        className="fixed inset-0 pointer-events-none"
        style={{ background: 'radial-gradient(ellipse 60% 40% at 50% -10%, rgba(6,182,212,0.10) 0%, transparent 70%)' }}
      />
      <div className="max-w-md w-full relative z-10">
        <div className="text-center mb-12">
          <div className="text-6xl mb-4 animate-bounce">🔍</div>
          <h2 className="text-3xl font-bold text-foreground mb-2">Deepfake Analysis</h2>
          <p className="text-primary font-mono text-sm animate-pulse uppercase tracking-widest">{status}...</p>
        </div>

        <div className="space-y-6 relative">
          <div className="absolute left-[27px] top-4 bottom-4 w-0.5 bg-border" />
          {steps.map((step, i) => {
            const isActive = i === activeStep;
            const isCompleted = i < activeStep;
            return (
              <div key={step.id} className={`flex items-center gap-6 transition-all duration-500 ${isActive ? 'scale-105 opacity-100' : isCompleted ? 'opacity-50' : 'opacity-30'}`}>
                <div className={`z-10 w-14 h-14 rounded-2xl flex items-center justify-center text-2xl border-2 transition-all duration-500 ${
                  isActive ? 'bg-primary/20 border-primary shadow-[0_0_20px_hsl(var(--primary)/0.4)]' :
                  isCompleted ? 'bg-green-500/10 border-green-500' : 'bg-card border-border'}`}>
                  {isCompleted ? '✅' : step.icon}
                </div>
                <div className="flex-1">
                  <h3 className={`font-bold ${isActive ? 'text-foreground' : 'text-muted-foreground'}`}>{step.name}</h3>
                  {isActive && (
                    <div className="mt-1 flex gap-1 h-1 w-full bg-border rounded-full overflow-hidden">
                      <div className="h-full bg-primary rounded-full animate-pulse" style={{ width: '60%' }} />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-12 text-center text-xs text-muted-foreground uppercase tracking-[0.2em]">
          Running Multi-Modal Forensic Scan
        </div>
      </div>
    </div>
  );

  // ── ERROR STATE ───────────────────────────────────────────────────────────
  if (error) return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="text-center bg-card border border-red-500/30 p-12 rounded-3xl max-w-md w-full">
        <div className="text-6xl mb-6">⚠️</div>
        <h2 className="text-2xl font-bold text-foreground mb-4">Analysis Interrupted</h2>
        <p className="text-muted-foreground mb-8 leading-relaxed">{error}</p>
        <button
          onClick={() => router.push('/deepfake-detector')}
          className="w-full py-4 bg-destructive hover:opacity-90 text-white rounded-xl font-bold transition-opacity"
        >
          Return to Detector
        </button>
      </div>
    </div>
  );

  // ── RESULTS ───────────────────────────────────────────────────────────────
  const score = result?.score || 0;
  const isDeepfake = score > 70;
  const isMedium = score > 40 && score <= 70;
  const heatmapUrl: string | null = result?.heatmap_url ? `${API_BASE}${result.heatmap_url}` : null;

  const verdictConfig = isDeepfake
    ? { emoji: '🚨', label: 'DEEPFAKE DETECTED!', border: 'border-red-500/50', bg: 'bg-red-500/5', text: 'text-red-400', bar: 'bg-red-500' }
    : isMedium
    ? { emoji: '⚠️', label: 'SUSPICIOUS CONTENT', border: 'border-yellow-500/50', bg: 'bg-yellow-500/5', text: 'text-yellow-400', bar: 'bg-yellow-500' }
    : { emoji: '✅', label: 'LIKELY AUTHENTIC', border: 'border-green-500/50', bg: 'bg-green-500/5', text: 'text-green-400', bar: 'bg-green-500' };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Background glow */}
      <div
        className="fixed inset-0 pointer-events-none"
        style={{ background: 'radial-gradient(ellipse 60% 40% at 50% -10%, rgba(6,182,212,0.08) 0%, transparent 70%)' }}
      />

      <main className="relative z-10 max-w-3xl mx-auto px-4 py-14 space-y-6">

        {/* Header */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 bg-primary/10 border border-primary/20 text-primary rounded-full px-4 py-1.5 text-xs font-mono uppercase tracking-widest mb-4">
            🔍 Forensic Analysis Report
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-foreground">Analysis Results</h1>
          <p className="text-muted-foreground mt-2 font-mono text-sm">Scan ID: {scanId?.slice(0, 8)}...</p>
        </div>

        {/* VERDICT CARD */}
        <div className={`rounded-2xl border ${verdictConfig.border} ${verdictConfig.bg} p-8 text-center`}>
          <div className="text-6xl mb-4">{verdictConfig.emoji}</div>
          <h2 className={`text-3xl font-extrabold mb-2 ${verdictConfig.text}`}>{verdictConfig.label}</h2>
          <p className="text-muted-foreground text-sm">Risk Level: <span className={`font-bold ${verdictConfig.text}`}>{result?.risk_level?.toUpperCase() || '—'}</span></p>
        </div>

        {/* SCORE CARD */}
        <div className="bg-card rounded-2xl border border-border p-6">
          <h3 className="text-lg font-bold mb-4 text-foreground">📊 Deepfake Score</h3>
          <div className="flex items-center gap-4 mb-3">
            <div className={`text-5xl font-extrabold ${verdictConfig.text}`}>{score?.toFixed(1)}%</div>
            <div className="flex-1">
              <div className="w-full bg-secondary rounded-full h-4 overflow-hidden">
                <div
                  className={`h-4 rounded-full transition-all duration-1000 ${verdictConfig.bar}`}
                  style={{ width: `${score}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground mt-1">
                <span>0% Authentic</span>
                <span>100% Deepfake</span>
              </div>
            </div>
          </div>
          <p className="text-muted-foreground text-sm">
            Confidence: <span className="text-foreground font-bold">{result?.confidence?.toFixed(1)}%</span>
          </p>
        </div>

        {/* HEATMAP (if available) */}
        {heatmapUrl && (
          <div className="bg-card rounded-2xl border border-border p-6">
            <h3 className="text-lg font-bold mb-4 text-foreground">🗺️ Manipulation Heatmap</h3>
            <div className="rounded-xl overflow-hidden border border-border">
              <img
                src={heatmapUrl}
                alt="Deepfake manipulation heatmap"
                className="w-full object-contain max-h-64"
                onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
              />
            </div>
            <p className="text-xs text-muted-foreground mt-3">
              🔴 Red areas indicate regions most likely to be manipulated
            </p>
          </div>
        )}



        {/* ARTIFACTS */}
        {result?.artifacts_found?.length > 0 && (
          <div className="bg-card rounded-2xl border border-border p-6">
            <h3 className="text-lg font-bold mb-4 text-foreground">🔍 Artifacts Detected</h3>
            <ul className="space-y-2">
              {result.artifacts_found.map((artifact: string, i: number) => (
                <li key={i} className="flex items-center gap-3 py-2 px-3 rounded-lg bg-secondary border border-border">
                  <span className="text-red-400">⚠️</span>
                  <span className="text-sm text-foreground capitalize">{artifact.replace(/_/g, ' ')}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* MODEL SCORES */}
        {result?.model_scores && Object.keys(result.model_scores).length > 0 && (
          <div className="bg-card rounded-2xl border border-border p-6">
            <h3 className="text-lg font-bold mb-4 text-foreground">🤖 AI Model Breakdown</h3>
            <div className="space-y-4">
              {Object.entries(result.model_scores).map(([model, modelScore]: any) => (
                <div key={model}>
                  <div className="flex justify-between mb-1.5">
                    <span className="text-sm text-muted-foreground capitalize">{model.replace(/_/g, ' ')}</span>
                    <span className={`text-sm font-bold ${modelScore > 70 ? 'text-red-400' : modelScore > 40 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {modelScore?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-2 rounded-full transition-all duration-700 ${modelScore > 70 ? 'bg-red-500' : modelScore > 40 ? 'bg-yellow-500' : 'bg-green-500'}`}
                      style={{ width: `${Math.min(modelScore, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ACTION BUTTONS */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => router.push('/deepfake-detector')}
            className="py-3.5 bg-primary hover:opacity-90 text-white rounded-xl font-bold transition-opacity"
          >
            Analyze Another
          </button>
          <button
            onClick={() => router.push('/history')}
            className="py-3.5 bg-secondary hover:bg-secondary/80 border border-border text-foreground rounded-xl font-bold transition-colors"
          >
            View History
          </button>
          <button
            onClick={() => window.print()}
            className="col-span-2 py-3.5 bg-card hover:bg-secondary border border-border text-foreground rounded-xl font-bold transition-colors flex items-center justify-center gap-2"
          >
            🖨️ Print Full Case Report
          </button>
          <button
            onClick={() => {
              const text = `Trustora Forensic Report\nCase ID: ${scanId}\nVerdict: ${verdictConfig.label}`;
              navigator.clipboard.writeText(text);
              alert("Case summary copied to clipboard!");
            }}
            className="col-span-2 py-2 text-xs text-muted-foreground hover:text-primary transition-colors flex items-center justify-center gap-2"
          >
            🔗 Copy Case ID & Summary
          </button>
        </div>

      </main>
    </div>
  );
}
