'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import {
  ShieldCheck,
  ShieldX,
  Copy,
  Printer,
  Lock,
  FileAudio,
  ClipboardList,
  CheckCircle2,
  Clock,
  Hash,
  Fingerprint,
} from 'lucide-react';

// -------------------------------------------------------
// Types
// -------------------------------------------------------
interface EvidenceData {
  capture_id: string;
  blockchain_hash: string;
  sealed_at: string;
  status: string;
  is_verified: boolean;
  verification_message: string;
  file_url?: string;
  metadata?: Record<string, unknown>;
}

// -------------------------------------------------------
// Helper: format ISO timestamp to readable date-time
// -------------------------------------------------------
function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
      timeZoneName: 'short',
    });
  } catch {
    return iso;
  }
}

// -------------------------------------------------------
// Helper: derive a timestamp from capture_id for filename
// -------------------------------------------------------
function evidenceFilename(captureId: string): string {
  // Fall back to current time if id is not numeric
  const ts = isNaN(Number(captureId)) ? Date.now() : Number(captureId);
  return `evidence-${ts}.mp3`;
}

// -------------------------------------------------------
// Component
// -------------------------------------------------------
export default function EvidenceDetailPage() {
  const params = useParams();
  const captureId = params?.id as string;

  const [loading, setLoading] = useState<boolean>(true);
  const [data, setData] = useState<EvidenceData | null>(null);
  const [error, setError] = useState<string>('');
  const [copied, setCopied] = useState<boolean>(false);

  // Fetch evidence data on mount
  useEffect(() => {
    if (!captureId) {
      setError('No capture ID found in URL.');
      setLoading(false);
      return;
    }

    const token =
      typeof window !== 'undefined' ? localStorage.getItem('token') : null;

    if (!token) {
      setError('Authentication required. Please log in first.');
      setLoading(false);
      return;
    }

    const fetchEvidence = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/capture/verify/${captureId}`,
          {
            method: 'GET',
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(
            errData?.detail || `Server returned ${response.status}`
          );
        }

        const json: EvidenceData = await response.json();
        setData(json);
      } catch (err: any) {
        setError(err?.message || 'Failed to fetch evidence. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchEvidence();
  }, [captureId]);

  // Copy hash to clipboard
  const handleCopyHash = async () => {
    if (!data?.blockchain_hash) return;
    try {
      await navigator.clipboard.writeText(data.blockchain_hash);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      // fallback for unsupported browsers
      const el = document.createElement('textarea');
      el.value = data.blockchain_hash;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  // -------------------------------------------------------
  // LOADING STATE
  // -------------------------------------------------------
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center">
        <div className="text-center space-y-6">
          <div className="relative w-20 h-20 mx-auto">
            <div className="absolute inset-0 rounded-full border-4 border-cyan-500/20 animate-ping" />
            <div className="absolute inset-2 rounded-full border-4 border-t-cyan-400 border-r-transparent border-b-transparent border-l-transparent animate-spin" />
            <Lock className="absolute inset-0 m-auto w-7 h-7 text-cyan-400" />
          </div>
          <p className="text-gray-400 font-mono text-sm tracking-widest uppercase animate-pulse">
            Loading evidence...
          </p>
        </div>
      </div>
    );
  }

  // -------------------------------------------------------
  // ERROR STATE
  // -------------------------------------------------------
  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 flex items-center justify-center px-4">
        <div className="text-center max-w-md space-y-6">
          <div className="w-20 h-20 rounded-full bg-red-500/10 border border-red-500/30 flex items-center justify-center mx-auto">
            <ShieldX className="w-10 h-10 text-red-400" />
          </div>
          <h2 className="text-2xl font-bold text-white">Verification Failed</h2>
          <p className="text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-5 py-3 font-mono text-sm">
            {error}
          </p>
          <button
            onClick={() => window.history.back()}
            className="px-6 py-2.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-xl text-sm font-semibold transition-colors"
          >
            ← Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const isVerified = data.is_verified;
  const filename = evidenceFilename(data.capture_id || captureId);
  const formattedDate = formatTimestamp(data.sealed_at);

  // -------------------------------------------------------
  // MAIN RENDER
  // -------------------------------------------------------
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* ---- Background glow ---- */}
      <div
        className="fixed inset-0 pointer-events-none"
        aria-hidden="true"
        style={{
          background:
            'radial-gradient(ellipse 60% 40% at 50% -10%, rgba(6,182,212,0.12) 0%, transparent 70%)',
        }}
      />

      <main className="relative z-10 max-w-4xl mx-auto px-4 py-14 space-y-8">

        {/* ============================================
            A. HEADER
        ============================================ */}
        <header className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded-full px-4 py-1.5 text-xs font-mono uppercase tracking-widest mb-4">
            <Lock className="w-3.5 h-3.5" />
            Blockchain Secured
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-cyan-300 to-white bg-clip-text text-transparent">
            🔒 Digital Evidence
          </h1>
          <p className="text-gray-400 text-sm font-mono tracking-widest uppercase">
            Blockchain-Verified Capture
          </p>
        </header>

        {/* ============================================
            B. VERIFICATION STATUS CARD
        ============================================ */}
        <section
          className={`rounded-2xl border p-8 text-center space-y-4 transition-all ${
            isVerified
              ? 'bg-green-500/5 border-green-500/30 shadow-[0_0_40px_rgba(34,197,94,0.08)]'
              : 'bg-red-500/5 border-red-500/30 shadow-[0_0_40px_rgba(239,68,68,0.08)]'
          }`}
        >
          <div
            className={`w-24 h-24 rounded-full flex items-center justify-center mx-auto border-4 ${
              isVerified
                ? 'bg-green-500/10 border-green-500/30'
                : 'bg-red-500/10 border-red-500/30'
            }`}
          >
            {isVerified ? (
              <ShieldCheck className="w-12 h-12 text-green-400" />
            ) : (
              <ShieldX className="w-12 h-12 text-red-400" />
            )}
          </div>
          <div>
            <p
              className={`text-3xl font-extrabold tracking-tight ${
                isVerified ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {isVerified ? '✅ Verified' : '❌ Not Verified'}
            </p>
            <p className="text-gray-400 mt-2 text-sm max-w-md mx-auto leading-relaxed">
              {data.verification_message ||
                (isVerified
                  ? 'This evidence has been cryptographically verified on the blockchain.'
                  : 'Evidence integrity check failed. The file may have been tampered with.')}
            </p>
          </div>
        </section>

        {/* ============================================
            C. EVIDENCE INFORMATION CARD
        ============================================ */}
        <section className="bg-gray-900 rounded-2xl border border-gray-800 p-6 space-y-5">
          <h2 className="text-lg font-bold flex items-center gap-2 text-white">
            <Fingerprint className="w-5 h-5 text-cyan-400" />
            Evidence Information
          </h2>

          {/* Capture ID */}
          <div className="space-y-1.5">
            <label className="text-xs text-gray-500 uppercase tracking-widest font-mono">
              Capture ID
            </label>
            <div className="bg-gray-950 rounded-xl border border-gray-800 px-4 py-3 font-mono text-sm text-white break-all">
              {data.capture_id || captureId}
            </div>
          </div>

          {/* Blockchain Hash */}
          <div className="space-y-1.5">
            <label className="text-xs text-gray-500 uppercase tracking-widest font-mono flex items-center gap-1.5">
              <Hash className="w-3.5 h-3.5" /> SHA-256 Blockchain Hash
            </label>
            <div className="bg-gray-950 rounded-xl border border-gray-800 px-4 py-3 font-mono text-[11px] text-cyan-400 break-all leading-relaxed">
              {data.blockchain_hash}
            </div>
          </div>

          {/* Sealed At */}
          <div className="space-y-1.5">
            <label className="text-xs text-gray-500 uppercase tracking-widest font-mono flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" /> Sealed At
            </label>
            <div className="bg-gray-950 rounded-xl border border-gray-800 px-4 py-3 text-sm text-gray-200">
              {formattedDate}
            </div>
          </div>

          {/* Status */}
          <div className="space-y-1.5">
            <label className="text-xs text-gray-500 uppercase tracking-widest font-mono">
              Status
            </label>
            <div>
              <span className="inline-block bg-green-500/10 border border-green-500/20 text-green-400 font-extrabold text-sm uppercase tracking-widest px-4 py-2 rounded-lg">
                {data.status || 'AUTHENTIC'}
              </span>
            </div>
          </div>
        </section>

        {/* ============================================
            D. AUDIO PLAYER CARD (conditional)
        ============================================ */}
        {data.file_url && (
          <section className="bg-gray-900 rounded-2xl border border-gray-800 p-6 space-y-4">
            <h2 className="text-lg font-bold flex items-center gap-2 text-white">
              <FileAudio className="w-5 h-5 text-cyan-400" />
              🎵 Evidence File
            </h2>
            <div className="bg-gray-950 rounded-xl border border-gray-800 p-4 space-y-3">
              <p className="text-xs text-gray-500 font-mono tracking-wider uppercase">
                Filename
              </p>
              <p className="text-sm font-mono text-gray-300">{filename}</p>
              <audio
                controls
                className="w-full mt-2 rounded-lg accent-cyan-400"
                style={{ colorScheme: 'dark' }}
              >
                <source src={data.file_url} />
                Your browser does not support the audio element.
              </audio>
            </div>
          </section>
        )}

        {/* ============================================
            E. METADATA CARD (conditional)
        ============================================ */}
        {data.metadata && Object.keys(data.metadata).length > 0 && (
          <section className="bg-gray-900 rounded-2xl border border-gray-800 p-6 space-y-4">
            <h2 className="text-lg font-bold flex items-center gap-2 text-white">
              <ClipboardList className="w-5 h-5 text-cyan-400" />
              📊 Metadata
            </h2>
            <pre className="bg-gray-950 rounded-xl border border-gray-800 p-4 overflow-x-auto font-mono text-xs text-cyan-300 leading-relaxed whitespace-pre-wrap break-all">
              {JSON.stringify(data.metadata, null, 2)}
            </pre>
          </section>
        )}

        {/* ============================================
            F. INFORMATION CARD
        ============================================ */}
        <section className="bg-gray-900 rounded-2xl border border-gray-800 p-6 space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2 text-white">
            <Lock className="w-5 h-5 text-cyan-400" />
            🔐 How This Works
          </h2>
          <ul className="space-y-3">
            {[
              {
                icon: <Hash className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />,
                title: 'Cryptographic Hashing',
                desc: 'Every file is hashed using SHA-256, creating a unique fingerprint that detects any modification.',
              },
              {
                icon: <CheckCircle2 className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />,
                title: 'Blockchain Timestamping',
                desc: "The hash is anchored to the blockchain at capture time, creating an immutable and auditable timestamp.",
              },
              {
                icon: <ShieldCheck className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />,
                title: 'Integrity Verification',
                desc: 'Any alteration to the file — even a single byte — will cause the hash to change, instantly flagging tampering.',
              },
              {
                icon: <Fingerprint className="w-4 h-4 text-cyan-400 flex-shrink-0 mt-0.5" />,
                title: 'Legal Admissibility',
                desc: 'Blockchain-anchored evidence with a verifiable chain of custody meets digital forensics standards for court admissibility.',
              },
            ].map(({ icon, title, desc }) => (
              <li key={title} className="flex gap-3">
                {icon}
                <div>
                  <span className="text-sm font-semibold text-gray-200">
                    {title}:
                  </span>{' '}
                  <span className="text-sm text-gray-400">{desc}</span>
                </div>
              </li>
            ))}
          </ul>
        </section>

        {/* ============================================
            G. ACTION BUTTONS
        ============================================ */}
        <div className="grid grid-cols-2 gap-4">
          {/* Print Certificate */}
          <button
            onClick={() => window.print()}
            className="flex items-center justify-center gap-2.5 py-3.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-gray-600 rounded-2xl text-sm font-bold text-gray-200 transition-all duration-200 active:scale-95"
          >
            <Printer className="w-4 h-4" />
            🖨️ Print Certificate
          </button>

          {/* Copy Hash */}
          <button
            onClick={handleCopyHash}
            className={`flex items-center justify-center gap-2.5 py-3.5 rounded-2xl text-sm font-bold transition-all duration-200 active:scale-95 border ${
              copied
                ? 'bg-green-500/10 border-green-500/30 text-green-400'
                : 'bg-cyan-500/10 hover:bg-cyan-500/20 border-cyan-500/30 text-cyan-400 hover:border-cyan-500/50'
            }`}
          >
            <Copy className="w-4 h-4" />
            {copied ? '✅ Copied!' : '📋 Copy Hash'}
          </button>
        </div>

        {/* Footer note */}
        <p className="text-center text-xs text-gray-600 font-mono pb-4">
          TRUSTORA · Blockchain-Verified Digital Evidence System
        </p>
      </main>

      {/* ---- Print styles ---- */}
      <style>{`
        @media print {
          body { background: white !important; color: black !important; }
          button { display: none !important; }
          .fixed { display: none !important; }
          * { box-shadow: none !important; }
        }
      `}</style>
    </div>
  );
}
