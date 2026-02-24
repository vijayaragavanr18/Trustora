"use client";

import { Navbar } from "@/components/Navbar";
import { CameraCapture } from "@/components/CameraCapture";
import { Lock, ShieldCheck, Database, FileText, CheckCircle2, History as HistoryIcon, Camera, Video, Mic, Share2, Download, Trash2, Trash, RefreshCcw, ArrowLeft, X, ZoomIn } from "lucide-react";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Modal } from "@/components/Modal";
import { Button } from "@/components/ui/Button";

type Phase = 'selection' | 'capture' | 'security' | 'verification' | 'completed';

export default function DigitalEvidence() {
  const [phase, setPhase] = useState<Phase>('selection');
  const [evidenceType, setEvidenceType] = useState<'photo' | 'video' | 'audio' | null>(null);
  const [capturedEvidence, setCapturedEvidence] = useState<any[]>([]);
  const [binItems, setBinItems] = useState<any[]>([]);
  const [viewBin, setViewBin] = useState(false);
  const [loading, setLoading] = useState(false);
  const [currentScanId, setCurrentScanId] = useState<string | null>(null);
  const [capturedBlobUrl, setCapturedBlobUrl] = useState<string | null>(null);
  const [capturedFileType, setCapturedFileType] = useState<string>('photo');
  const [previewItem, setPreviewItem] = useState<any | null>(null);
  // Confirm destroy modal
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [isShredding, setIsShredding] = useState(false);

  const fetchHistory = async () => {
    try {
      if (api.isAuthenticated()) {
        const data = await api.getHistory();
        const binData = await api.getBin();

        const isEvidence = (item: any) =>
          item.file_name?.toLowerCase().startsWith('evidence-');

        const activeItems = data.filter(isEvidence);
        const binItemsRes = binData.filter(isEvidence);

        setCapturedEvidence(activeItems.slice(0, 8));
        setBinItems(binItemsRes);
      }
    } catch (e) {}
  };

  useEffect(() => {
    fetchHistory();
    const interval = setInterval(fetchHistory, 10000); // Background refresh
    return () => clearInterval(interval);
  }, [phase]);

  const handleTypeSelect = (type: 'photo' | 'video' | 'audio') => {
    if (!api.isAuthenticated()) {
      toast.error('Please log in first to capture secure evidence.');
      return;
    }
    setEvidenceType(type);
    setPhase('capture');
  };

  const handleCapture = async (blob: Blob) => {
    try {
      setPhase('security');

      // Store blob URL immediately so we can preview on completion
      const localUrl = URL.createObjectURL(blob);
      setCapturedBlobUrl(localUrl);
      setCapturedFileType(evidenceType || 'photo');

      const fileName = `evidence-${Date.now()}.${evidenceType === 'photo' ? 'jpg' : evidenceType === 'audio' ? 'mp3' : 'webm'}`;
      const file = new File([blob], fileName, { type: blob.type });
      
      let uploadResponse;
      if (evidenceType === 'photo') uploadResponse = await api.uploadImage(file);
      else if (evidenceType === 'audio') uploadResponse = await api.uploadAudio(file);
      else uploadResponse = await api.uploadVideo(file);

      const scanId = uploadResponse.id || uploadResponse.data?.id;
      setCurrentScanId(scanId);

      await new Promise(r => setTimeout(r, 1500));
      setPhase('verification');
      await api.startAnalysis(scanId);
      
      // Verification Phase: Wait for AI Analysis to complete
      let status = 'processing';
      let checkCount = 0;
      while ((status === 'processing' || status === 'pending') && checkCount < 60) {
        await new Promise(r => setTimeout(r, 2000));
        const statusRes = await api.getAnalysisStatus(scanId);
        status = statusRes.status;
        checkCount++;
        if (status === 'completed' || status === 'failed') break;
      }
      
      setPhase('completed');
      fetchHistory();
      toast.success(status === 'completed' ? 'Evidence analyzed and sealed successfully!' : 'Evidence sealed (analysis pending)');
    } catch (error: any) {
      console.error('Evidence capture error:', error);
      const msg = error?.response?.data?.detail || error?.message || 'Upload failed';
      toast.error(`Failed to secure evidence: ${msg}`);
      setPhase('selection');
    }
  };

  // Move to bin (BACKEND soft delete)
  const softDelete = async (id: string) => {
    try {
      await api.deleteScan(id);
      toast.success('Moved to Recycle Bin');
      fetchHistory();
    } catch (e) {
      toast.error('Failed to move to bin');
    }
  };

  // Restore from bin (BACKEND restore)
  const restoreItem = async (id: string) => {
    try {
      await api.restoreScan(id);
      toast.success('Item restored to Locker');
      fetchHistory();
    } catch (e) {
      toast.error('Failed to restore item');
    }
  };

  // Permanently delete: styled modal
  const permanentDelete = async (id: string) => {
    setConfirmDeleteId(id);
  };

  const doShred = async () => {
    if (!confirmDeleteId) return;
    setIsShredding(true);
    try {
      await api.permanentDeleteScan(confirmDeleteId);
      toast.success('Evidence destroyed permanently');
      fetchHistory();
    } catch (e) {
      toast.error('Failed to destroy item');
    } finally {
      setIsShredding(false);
      setConfirmDeleteId(null);
    }
  };

  const handleShare = async (item: any) => {
    const shareUrl = `${window.location.origin}/evidence/${item.id}`;
    const shareText = `Trustora Sealed Evidence\nIntegrity Hash: ${item.id}\nVerify at: ${shareUrl}`;
    const shareData = {
      title: 'Trustora Sealed Evidence',
      text: shareText,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
      } catch (e) {
        toast.error('Sharing cancelled');
      }
    } else {
      await navigator.clipboard.writeText(shareText);
      toast.success('Integrity secure link copied to clipboard!');
    }
  };

  return (
    <>
    {/* ---- Confirm Permanent Delete Modal ---- */}
    <Modal
      isOpen={!!confirmDeleteId}
      onClose={() => !isShredding && setConfirmDeleteId(null)}
      title="Permanently Destroy Evidence"
    >
      <div className="space-y-5">
        <p className="text-sm text-muted-foreground leading-relaxed">
          This evidence will be <span className="text-destructive font-semibold">permanently destroyed</span>.
          This action is irreversible and cannot be undone.
        </p>
        <div className="flex gap-3 justify-end">
          <Button
            variant="ghost"
            type="button"
            className="border border-primary/60"
            onClick={() => setConfirmDeleteId(null)}
          >
            Cancel
          </Button>
          <Button
            variant="danger"
            type="button"
            className="border border-primary/60"
            isLoading={isShredding}
            onClick={doShred}
          >
            Yes, Destroy It
          </Button>
        </div>
      </div>
    </Modal>
    <AnimatePresence>
      {previewItem && (
        <MediaPreviewModal item={previewItem} onClose={() => setPreviewItem(null)} />
      )}
    </AnimatePresence>
    <div className="min-h-screen bg-background text-foreground selection:bg-primary/30 font-sans">
      <Navbar />
      
      <main className="container mx-auto px-6 py-12 max-w-6xl">
        
        {/* PIPELINE SECTION */}
        {!viewBin && (
        <section className="mb-20">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-white via-cyan-400 to-white bg-clip-text text-transparent">
              Trusted Evidence Capture
            </h1>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Cryptographically secure evidence collection with blockchain timestamping.
            </p>
          </div>

          <div className="bg-card border border-border rounded-[2.5rem] p-8 md:p-12 relative overflow-hidden backdrop-blur-xl shadow-2xl">
            <AnimatePresence mode="wait">
              {phase === 'selection' && (
                <motion.div 
                  key="selection" 
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }} 
                  exit={{ opacity: 0, y: -10 }} 
                  className="grid grid-cols-1 md:grid-cols-3 gap-6"
                >
                  <SelectionCard 
                    icon={<Camera className="w-8 h-8" />} 
                    title="Capture Photo" 
                    desc="Instant high-res snapshot with metadata sealing" 
                    onClick={() => handleTypeSelect('photo')} 
                  />
                  <SelectionCard 
                    icon={<Video className="w-8 h-8" />} 
                    title="Capture Video" 
                    desc="Secure video recording with continuous hashing" 
                    onClick={() => handleTypeSelect('video')} 
                  />
                  <SelectionCard 
                    icon={<Mic className="w-8 h-8" />} 
                    title="Capture Audio" 
                    desc="Tamper-proof audio evidence with voice analysis" 
                    onClick={() => handleTypeSelect('audio')} 
                  />
                </motion.div>
              )}

              {phase === 'capture' && (
                <motion.div key="capture" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="space-y-6">
                  <div className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-cyan-400 font-mono text-[10px] uppercase tracking-[0.2em]"><div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" /> Live Node Active</span>
                    <button onClick={() => setPhase('selection')} className="text-xs text-gray-500 hover:text-white underline underline-offset-4">Quit Session</button>
                  </div>
                  <CameraCapture onCapture={handleCapture} mode={evidenceType || 'video'} />
                </motion.div>
              )}

              {phase === 'security' && (
                <motion.div key="security" className="flex flex-col items-center justify-center py-20 text-center">
                  <Database className="w-20 h-20 text-cyan-500 animate-bounce mb-8" />
                  <h2 className="text-2xl font-bold mb-2 uppercase tracking-widest text-cyan-400">Security Phase</h2>
                  <p className="text-gray-400 text-sm">Binding SHA-256 metadata signature...</p>
                </motion.div>
              )}

              {phase === 'verification' && (
                <motion.div key="verification" className="flex flex-col items-center justify-center py-20 text-center">
                  <ShieldCheck className="w-20 h-20 text-emerald-500 animate-pulse mb-8" />
                  <h2 className="text-2xl font-bold mb-2 uppercase tracking-widest text-emerald-400">Verification Phase</h2>
                  <p className="text-gray-400 text-sm">Validating authenticity anchor...</p>
                </motion.div>
              )}

              {phase === 'completed' && (
                <motion.div key="completed" className="text-center py-12">
                  <div className="w-20 h-20 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center mx-auto mb-6"><CheckCircle2 className="w-10 h-10" /></div>
                  <h2 className="text-3xl font-bold mb-2 text-white">Evidence Sealed</h2>
                  <p className="text-gray-400 mb-8 text-sm font-mono uppercase">Reference ID: {currentScanId?.slice(0, 16)}</p>
                  <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <button
                      onClick={() => {
                        // Preview the captured evidence (use local blob URL for instant display)
                        setPreviewItem({
                          id: currentScanId,
                          file_name: `evidence-${currentScanId?.slice(0, 8)}`,
                          file_url: capturedBlobUrl,
                          file_type: capturedFileType,
                          created_at: new Date().toISOString(),
                        });
                      }}
                      className="px-8 py-3 bg-cyan-500 hover:bg-cyan-600 rounded-xl font-bold"
                    >
                      View Evidence
                    </button>
                    <button
                      onClick={() => {
                        if (capturedBlobUrl) URL.revokeObjectURL(capturedBlobUrl);
                        setCapturedBlobUrl(null);
                        setPhase('selection');
                      }}
                      className="px-8 py-3 bg-secondary hover:bg-secondary/80 rounded-xl font-bold"
                    >
                      Capture Again
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </section>
        )}

        {/* LOCKER / BIN SECTION */}
        <section className="mt-12">
          <div className="flex items-center justify-between mb-8 border-b border-border pb-4">
             <div className="flex items-center gap-3">
               {viewBin ? <Trash className="w-6 h-6 text-red-500" /> : <HistoryIcon className="w-6 h-6 text-cyan-400" />}
               <h2 className="text-2xl font-bold">{viewBin ? 'Recycle Bin' : 'Evidence Locker'}</h2>
             </div>
             
             <div className="flex items-center gap-4">
                <button 
                  onClick={() => setViewBin(!viewBin)}
                  suppressHydrationWarning
                  className={`text-xs font-bold uppercase tracking-widest px-4 py-2 rounded-full border transition-all flex items-center gap-2 ${viewBin ? 'bg-cyan-500/10 border-cyan-500/30 text-cyan-500 hover:bg-cyan-500/20' : 'bg-red-500/10 border-red-500/30 text-red-500 hover:bg-red-500/20'}`}
                >
                  {viewBin ? <><ArrowLeft size={14} /> Back to Locker</> : <><Trash size={14} /> View Bin ({binItems.length})</>}
                </button>
             </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence mode="popLayout">
              {viewBin ? (
                binItems.length === 0 ? (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="col-span-full py-12 text-center text-muted-foreground font-mono text-sm uppercase tracking-widest italic">Bin is empty</motion.div>
                ) : (
                  binItems.map((item, i) => (
                    <EvidenceCard 
                      key={item.id} 
                      item={item} 
                      index={i} 
                      isBin 
                      onRestore={() => restoreItem(item.id)} 
                      onDelete={() => permanentDelete(item.id)} 
                    />
                  ))
                )
              ) : (
                capturedEvidence.length === 0 ? (
                  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="col-span-full py-12 text-center text-muted-foreground font-mono text-sm uppercase tracking-widest italic">No evidence in locker</motion.div>
                ) : (
                  capturedEvidence.map((item, i) => (
                    <EvidenceCard 
                      key={item.id} 
                      item={item} 
                      index={i} 
                      onDelete={() => softDelete(item.id)} 
                      onShare={() => handleShare(item)} 
                      onPreview={setPreviewItem}
                    />
                  ))
                )
              )}
            </AnimatePresence>
          </div>
        </section>

      </main>
    </div>
    </>
  );
}

function SelectionCard({ icon, title, desc, onClick }: any) {
  return (
    <button 
      onClick={onClick} 
      suppressHydrationWarning
      className="group p-8 bg-card border border-border rounded-3xl text-left hover:border-primary/50 hover:bg-secondary transition-all duration-300 relative overflow-hidden"
    >
      <div className="w-14 h-14 bg-secondary rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 group-hover:bg-primary/20 group-hover:text-primary transition-all">
        {icon}
      </div>
      <h3 className="text-xl font-bold mb-2">{title}</h3>
      <p className="text-gray-400 text-sm leading-relaxed">{desc}</p>
      <div className="absolute bottom-0 left-0 h-1 w-0 bg-primary group-hover:w-full transition-all duration-500" />
    </button>
  );
}

function EvidenceCard({ item, index, isBin, onDelete, onRestore, onShare, onPreview }: any) {
  const isHighRisk = item.risk_level === 'HIGH';
  const score = (item.deepfake_score !== undefined && item.deepfake_score !== null) ? Math.round(item.deepfake_score) : null;

  return (
    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} transition={{ delay: index * 0.05 }} className={`bg-card border rounded-2xl p-5 hover:bg-secondary transition-all group ${isBin ? 'border-red-500/10 hover:border-red-500/30' : 'border-border hover:border-primary/20'}`}>
      <div className="flex items-start justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center text-muted-foreground group-hover:text-primary transition-colors">
            {item.file_type === 'video' ? <Video size={18} /> : item.file_type === 'audio' ? <Mic size={18} /> : <Camera size={18} />}
          </div>
          <div className="min-w-0">
            <h4 className="font-bold text-sm truncate w-28 uppercase tracking-tight">{item.file_name?.replace('evidence-', '')}</h4>
            <div className="flex items-center gap-2">
              <p className="text-[9px] text-muted-foreground font-mono tracking-tighter uppercase">SIG: {item.id.slice(0, 8)}</p>
              {score !== null && (
                <span className={`text-[9px] font-bold px-1 rounded ${isHighRisk ? 'text-red-400' : 'text-green-400'}`}>
                  {score}% {item.risk_level}
                </span>
              )}
            </div>
          </div>
        </div>
        <div className={`px-2 py-0.5 rounded-full text-[9px] font-bold flex items-center gap-1 ${isBin ? 'bg-red-500/10 text-red-500 border border-red-500/20' : isHighRisk ? 'bg-red-500/10 text-red-500 border border-red-500/20' : 'bg-green-500/10 text-green-500 border border-green-500/20'}`}>
          {isBin ? 'DELETED' : isHighRisk ? 'TAMPEDED' : <><Lock size={10} /> SEALED</>}
        </div>
      </div>

      <div className="flex gap-2">
        {!isBin ? (
          <>
            {/* DATA: opens media preview instead of navigating to analysis */}
            <button suppressHydrationWarning onClick={() => onPreview(item)} className="flex-1 py-2 bg-secondary hover:bg-primary hover:text-primary-foreground rounded-lg text-[10px] font-bold transition-all flex items-center justify-center gap-2 uppercase tracking-widest"><FileText size={12} /> Data</button>
            <button suppressHydrationWarning onClick={onShare} className="p-2 bg-secondary hover:bg-secondary/80 rounded-lg transition-colors text-muted-foreground hover:text-foreground"><Share2 size={12} /></button>
            <button suppressHydrationWarning onClick={onDelete} className="p-2 bg-secondary hover:bg-red-500/20 hover:text-red-500 rounded-lg transition-colors"><Trash2 size={12} /></button>
          </>
        ) : (
          <>
            <button suppressHydrationWarning onClick={onRestore} className="flex-1 py-2 bg-emerald-500/10 hover:bg-emerald-500 hover:text-black rounded-lg text-[10px] font-bold transition-all flex items-center justify-center gap-2 uppercase tracking-widest text-emerald-500"><RefreshCcw size={12} /> Restore</button>
            <button suppressHydrationWarning onClick={onDelete} className="flex-1 py-2 bg-red-500/10 hover:bg-red-500 hover:text-white rounded-lg text-[10px] font-bold transition-all flex items-center justify-center gap-2 uppercase tracking-widest text-red-500"><Trash2 size={12} /> Shred</button>
          </>
        )}
      </div>
    </motion.div>
  );
}

// -------------------------------------------------------
// Media Preview Modal
// -------------------------------------------------------
function MediaPreviewModal({ item, onClose }: { item: any; onClose: () => void }) {
  const fileUrl = item.file_url
    ? (item.file_url.startsWith('http') || item.file_url.startsWith('blob:')
        ? item.file_url
        : `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${item.file_url}`)
    : null;
  const type: 'photo' | 'video' | 'audio' = item.file_type === 'video' ? 'video' : item.file_type === 'audio' ? 'audio' : 'photo';

  return (
    <motion.div
      key="modal-backdrop"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)' }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.92, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.92, opacity: 0, y: 20 }}
        transition={{ type: 'spring', damping: 20, stiffness: 300 }}
        className="bg-card border border-border rounded-[2rem] w-full max-w-2xl overflow-hidden shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-4 border-b border-border">
          <div>
            <div className="flex items-center gap-2">
              {type === 'video' ? <Video size={16} className="text-primary" /> : type === 'audio' ? <Mic size={16} className="text-primary" /> : <Camera size={16} className="text-primary" />}
              <h3 className="font-bold text-sm uppercase tracking-widest">{item.file_name || 'Evidence'}</h3>
            </div>
            <p className="text-[10px] text-muted-foreground font-mono mt-0.5">SIG: {item.id}</p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-secondary hover:bg-destructive/20 hover:text-destructive flex items-center justify-center transition-colors"
          >
            <X size={14} />
          </button>
        </div>

        {/* Media Content */}
        <div className="p-6 space-y-5">
          {!fileUrl ? (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <ZoomIn size={40} className="mb-3 opacity-30" />
              <p className="text-sm">No media file available</p>
            </div>
          ) : type === 'photo' ? (
            // Photo
            <div className="rounded-xl overflow-hidden bg-black border border-border">
              <img src={fileUrl} alt={item.file_name} className="w-full h-auto max-h-[60vh] object-contain" />
            </div>
          ) : type === 'video' ? (
            // Video — src directly on element (blob URLs require this)
            <div className="rounded-xl overflow-hidden bg-black border border-border">
              <video
                controls
                playsInline
                src={fileUrl}
                className="w-full max-h-[60vh]"
              />
            </div>
          ) : (
            // Audio — src directly on element (blob URLs require this)
            <div className="bg-secondary rounded-xl border border-border p-6 flex flex-col items-center gap-4">
              <div className="w-20 h-20 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center">
                <Mic size={32} className="text-primary animate-pulse" />
              </div>
              <p className="text-xs text-muted-foreground font-mono">{item.file_name}</p>
              <audio
                controls
                src={fileUrl}
                className="w-full"
              />
            </div>
          )}

          {/* Integrity Info */}
          <div className="bg-secondary rounded-xl border border-border p-4 space-y-2">
            <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-mono">Integrity Hash</p>
            <p className="font-mono text-xs text-primary break-all">{item.id}</p>
            {item.created_at && (
              <p className="text-[10px] text-muted-foreground font-mono">
                Sealed: {new Date(item.created_at).toLocaleString()}
              </p>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}
