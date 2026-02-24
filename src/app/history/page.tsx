"use client";

import { useEffect, useState, useRef } from "react";
import { Navbar } from "@/components/Navbar";
import {
  Search, Download, MoreHorizontal,
  FileImage, FileVideo, AlertTriangle, CheckCircle, FileAudio,
  Trash2, Eye, X, CheckSquare, Square, FolderDown
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/Modal";
import { Button } from "@/components/ui/Button";
import { toast } from "sonner";

const API_BASE = "http://localhost:8000";

export default function HistoryPage() {
  const router = useRouter();
  const [scans, setScans] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Dropdown (···) state
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  // Confirm delete modal
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Downloads modal
  const [downloadsOpen, setDownloadsOpen] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState<string>("");

  // Filters
  const [searchQuery, setSearchQuery] = useState("");
  const TYPE_OPTIONS = ['All', 'Image', 'Video', 'Audio'] as const;
  const [typeFilter, setTypeFilter] = useState<typeof TYPE_OPTIONS[number]>('All');
  const cycleType = () => {
    const idx = TYPE_OPTIONS.indexOf(typeFilter);
    setTypeFilter(TYPE_OPTIONS[(idx + 1) % TYPE_OPTIONS.length]);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpenMenuId(null);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      setError("");

      if (!api.isAuthenticated()) {
        router.push('/login');
        return;
      }

      const data = await api.getHistory();
      if (!Array.isArray(data)) { 
        setScans([]); 
        setLoading(false);
        return; 
      }

      const mappedScans = data.map((scan: any) => {
        try {
          // Normalize risk level
          let risk = "Unknown";
          if (scan.risk_level) {
            risk = scan.risk_level.charAt(0).toUpperCase() + scan.risk_level.slice(1).toLowerCase();
          }

          return {
            id: scan.id || 'unknown',
            name: scan.file_name || 'Untitled',
            file_url: scan.file_url || null,
            file_type: scan.file_type || 'unknown',
            date: scan.created_at
              ? new Date(scan.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
              : 'N/A',
            type: scan.file_type ? (scan.file_type.charAt(0).toUpperCase() + scan.file_type.slice(1)) : 'Unknown',
            risk: risk,
            score: typeof scan.deepfake_score === 'number' ? Math.round(scan.deepfake_score) : 0,
            status: scan.status || 'unknown'
          };
        } catch (e) { 
          console.error("Mapping error for scan:", scan, e);
          return null; 
        }
      }).filter(Boolean);

      setScans(mappedScans);
    } catch (err: any) {
      console.error("History fetch error:", err);
      setError(err.response?.data?.detail || err.message || "Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { 
    fetchHistory(); 
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ---- Filtered scans for table ----
  const filteredScans = scans.filter(scan => {
    const matchesSearch =
      searchQuery === '' ||
      scan.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scan.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType =
      typeFilter === 'All' || scan.type === typeFilter;
    return matchesSearch && matchesType;
  });

  // ---- Delete ----
  const doDelete = async () => {
    if (!confirmDeleteId) return;
    setIsDeleting(true);
    try {
      await api.deleteScan(confirmDeleteId);
      toast.success("Scan deleted successfully");
      setScans(prev => prev.filter(s => s.id !== confirmDeleteId));
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Failed to delete scan");
    } finally {
      setIsDeleting(false);
      setConfirmDeleteId(null);
    }
  };

  // ---- Downloads ----
  const toggleSelect = (id: string) => {
    setSelectedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    const downloadable = scans.filter(s => s.file_url);
    if (selectedIds.size === downloadable.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(downloadable.map(s => s.id)));
    }
  };

  const downloadFile = async (scan: any, index: number, total: number) => {
    const url = scan.file_url.startsWith('http')
      ? scan.file_url
      : `${API_BASE}${scan.file_url}`;

    setDownloadProgress(`Downloading ${index + 1} of ${total}: ${scan.name}`);

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Failed to fetch ${scan.name}`);
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = scan.name;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    } catch {
      toast.error(`Failed to download: ${scan.name}`);
    }
  };

  const handleDownloadSelected = async () => {
    const toDownload = scans.filter(s => selectedIds.has(s.id) && s.file_url);
    if (toDownload.length === 0) {
      toast.error("No downloadable files selected");
      return;
    }

    setIsDownloading(true);
    for (let i = 0; i < toDownload.length; i++) {
      await downloadFile(toDownload[i], i, toDownload.length);
      // Small delay between downloads so browser doesn't block them
      if (i < toDownload.length - 1) await new Promise(r => setTimeout(r, 600));
    }
    setIsDownloading(false);
    setDownloadProgress("");
    toast.success(`${toDownload.length} file${toDownload.length > 1 ? 's' : ''} downloaded!`);
    setDownloadsOpen(false);
    setSelectedIds(new Set());
  };

  const handleExportZip = async () => {
    if (selectedIds.size === 0) {
      toast.error("Please select at least one scan");
      return;
    }

    setIsDownloading(true);
    setDownloadProgress("Generating forensic Zip...");
    try {
      const blob = await api.batchExportScans(Array.from(selectedIds));
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `trustora_forensic_export_${new Date().getTime()}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast.success("Forensic Zip exported successfully!");
      setDownloadsOpen(false);
      setSelectedIds(new Set());
    } catch (e) {
      toast.error("Failed to generate export");
    } finally {
      setIsDownloading(false);
      setDownloadProgress("");
    }
  };

  const downloadableScans = scans.filter(s => s.file_url);

  return (
    <div className="min-h-screen bg-background bg-grid bg-radial-fade">
      <Navbar />
      <main className="container mx-auto px-6 py-12 max-w-6xl">

        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
          <div>
            <h1 className="font-display text-3xl font-bold text-foreground mb-1">Analysis History</h1>
            <p className="text-muted-foreground text-sm">Manage and review your past deepfake analysis reports.</p>
          </div>
          <div className="flex gap-2">
            <button
              suppressHydrationWarning
              onClick={() => { setDownloadsOpen(true); setSelectedIds(new Set()); }}
              className="flex items-center gap-2 px-4 py-2 bg-secondary border border-border rounded-lg text-sm font-medium hover:bg-primary/10 hover:border-primary/40 hover:text-primary transition-all"
            >
              <FolderDown className="w-4 h-4" />
              Downloads
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-500 text-sm">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        {/* Filters */}
        <div className="bg-card border border-border rounded-xl p-4 mb-8 flex flex-col md:flex-row gap-4 items-center justify-between">
          <div className="relative w-full md:w-96">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              suppressHydrationWarning
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search by filename or ID..."
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>
          <div className="flex gap-2 w-full md:w-auto">
            <button
              suppressHydrationWarning
              onClick={cycleType}
              className={`flex items-center gap-2 px-3 py-2 border rounded-lg text-xs font-medium transition-colors whitespace-nowrap ${
                typeFilter !== 'All'
                  ? 'bg-primary/10 border-primary/40 text-primary'
                  : 'bg-background border-border hover:bg-secondary'
              }`}
            >
              Type: {typeFilter}
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="bg-secondary/50 text-muted-foreground font-medium border-b border-border">
                <tr>
                  <th className="px-6 py-4">ID &amp; File</th>
                  <th className="px-6 py-4">Date Scanned</th>
                  <th className="px-6 py-4">Type</th>
                  <th className="px-6 py-4">Risk Level</th>
                  <th className="px-6 py-4">Confidence</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {loading ? (
                  <tr><td colSpan={6} className="px-6 py-8 text-center text-muted-foreground">Loading history...</td></tr>
                ) : filteredScans.length === 0 ? (
                  <tr><td colSpan={6} className="px-6 py-8 text-center text-muted-foreground">
                    {scans.length === 0 ? 'No analysis history found. Upload a file to get started.' : 'No results match your search.'}
                  </td></tr>
                ) : (
                  filteredScans.map((scan, i) => (
                    <motion.tr
                      key={scan.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="group hover:bg-secondary/30 transition-colors cursor-pointer"
                      onClick={() => router.push(`/analysis/${scan.id}`)}
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 rounded-lg bg-background border border-border">
                            {scan.type === 'Image' ? <FileImage className="w-5 h-5 text-blue-500" /> :
                             scan.type === 'Video' ? <FileVideo className="w-5 h-5 text-purple-500" /> :
                             <FileAudio className="w-5 h-5 text-yellow-500" />}
                          </div>
                          <div>
                            <div className="font-medium text-foreground">{scan.name}</div>
                            <div className="text-xs text-muted-foreground font-mono">{scan.id.slice(0, 8)}...</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">{scan.date}</td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-secondary text-foreground border border-border">
                          {scan.type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                          scan.risk === "High" || scan.risk === "Critical" ? "bg-red-500/10 border-red-500/20 text-red-500" :
                          scan.risk === "Medium"  ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-500" :
                          scan.risk === "Low"     ? "bg-green-500/10 border-green-500/20 text-green-500" :
                          "bg-gray-500/10 border-gray-500/20 text-gray-500"
                        }`}>
                          {(scan.risk === "High" || scan.risk === "Critical") && <AlertTriangle className="w-3 h-3" />}
                          {scan.risk === "Low" && <CheckCircle className="w-3 h-3" />}
                          {scan.risk}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${scan.score > 70 ? "bg-red-500" : scan.score > 40 ? "bg-yellow-500" : "bg-green-500"}`}
                              style={{ width: `${scan.score}%` }}
                            />
                          </div>
                          <span className="font-mono text-xs">{scan.score}%</span>
                        </div>
                      </td>

                      {/* Actions cell */}
                      <td className="px-6 py-4 text-right" onClick={e => e.stopPropagation()}>
                        <div className="relative inline-block" ref={openMenuId === scan.id ? menuRef : undefined}>
                          <button
                            suppressHydrationWarning
                            onClick={() => setOpenMenuId(openMenuId === scan.id ? null : scan.id)}
                            className="p-1.5 rounded-md hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
                          >
                            <MoreHorizontal className="w-4 h-4" />
                          </button>

                          <AnimatePresence>
                            {openMenuId === scan.id && (
                              <motion.div
                                initial={{ opacity: 0, scale: 0.92, y: -4 }}
                                animate={{ opacity: 1, scale: 1, y: 0 }}
                                exit={{ opacity: 0, scale: 0.92, y: -4 }}
                                transition={{ duration: 0.12 }}
                                className="absolute right-0 mt-1 w-44 bg-card border border-border rounded-xl shadow-2xl z-50 overflow-hidden"
                              >
                                <button
                                  suppressHydrationWarning
                                  onClick={() => { setOpenMenuId(null); router.push(`/analysis/${scan.id}`); }}
                                  className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-foreground hover:bg-secondary transition-colors text-left"
                                >
                                  <Eye className="w-4 h-4 text-primary" /> View Report
                                </button>
                                {scan.file_url && (
                                  <button
                                    suppressHydrationWarning
                                    onClick={() => {
                                      setOpenMenuId(null);
                                      downloadFile(scan, 0, 1);
                                    }}
                                    className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-foreground hover:bg-secondary transition-colors text-left"
                                  >
                                    <Download className="w-4 h-4 text-primary" /> Download
                                  </button>
                                )}
                                <div className="border-t border-border" />
                                <button
                                  suppressHydrationWarning
                                  onClick={() => { setOpenMenuId(null); setConfirmDeleteId(scan.id); }}
                                  className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-red-400 hover:bg-red-500/10 transition-colors text-left"
                                >
                                  <Trash2 className="w-4 h-4" /> Delete
                                </button>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          {!loading && scans.length > 0 && (
            <div className="p-4 border-t border-border bg-secondary/10 flex justify-center">
              <button suppressHydrationWarning className="text-sm text-primary hover:underline">View All History</button>
            </div>
          )}
        </div>
      </main>

      {/* ========== DOWNLOADS MODAL ========== */}
      {downloadsOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={() => !isDownloading && setDownloadsOpen(false)}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94 }}
            className="bg-card border border-border w-full max-w-lg rounded-2xl shadow-2xl overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal header */}
            <div className="px-6 py-4 border-b border-border flex items-center justify-between bg-secondary/20">
              <div className="flex items-center gap-2">
                <FolderDown className="w-5 h-5 text-primary" />
                <h3 className="font-semibold text-foreground">Download Files</h3>
              </div>
              <button
                onClick={() => !isDownloading && setDownloadsOpen(false)}
                className="p-1 hover:bg-secondary rounded-lg transition-colors text-muted-foreground"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Select all */}
            <div className="px-6 py-3 border-b border-border flex items-center justify-between bg-secondary/10">
              <span className="text-xs text-muted-foreground">
                {selectedIds.size} of {downloadableScans.length} selected
              </span>
              <button
                suppressHydrationWarning
                onClick={toggleSelectAll}
                className="flex items-center gap-1.5 text-xs font-medium text-primary hover:underline"
              >
                {selectedIds.size === downloadableScans.length && downloadableScans.length > 0
                  ? <><CheckSquare className="w-3.5 h-3.5" /> Deselect All</>
                  : <><Square className="w-3.5 h-3.5" /> Select All</>
                }
              </button>
            </div>

            {/* File list */}
            <div className="max-h-72 overflow-y-auto divide-y divide-border">
              {downloadableScans.length === 0 ? (
                <div className="px-6 py-10 text-center text-muted-foreground text-sm">
                  No downloadable files found.
                </div>
              ) : (
                downloadableScans.map(scan => (
                  <label
                    key={scan.id}
                    className={`flex items-center gap-3 px-6 py-3 cursor-pointer hover:bg-secondary/40 transition-colors ${selectedIds.has(scan.id) ? 'bg-primary/5' : ''}`}
                  >
                    {/* Checkbox */}
                    <div
                      onClick={() => toggleSelect(scan.id)}
                      className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 transition-colors ${
                        selectedIds.has(scan.id)
                          ? 'bg-primary border-primary'
                          : 'border-border bg-background'
                      }`}
                    >
                      {selectedIds.has(scan.id) && (
                        <svg className="w-2.5 h-2.5 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>

                    {/* File icon */}
                    <div className="p-1.5 rounded-md bg-background border border-border flex-shrink-0">
                      {scan.file_type === 'video' ? <FileVideo className="w-4 h-4 text-purple-500" /> :
                       scan.file_type === 'audio' ? <FileAudio className="w-4 h-4 text-yellow-500" /> :
                       <FileImage className="w-4 h-4 text-blue-500" />}
                    </div>

                    {/* File info */}
                    <div className="flex-1 min-w-0" onClick={() => toggleSelect(scan.id)}>
                      <p className="text-sm font-medium text-foreground truncate">{scan.name}</p>
                      <p className="text-[11px] text-muted-foreground font-mono">{scan.date}</p>
                    </div>
                  </label>
                ))
              )}
            </div>

            {/* Progress */}
            {isDownloading && downloadProgress && (
              <div className="px-6 py-2 bg-primary/5 border-t border-primary/10">
                <p className="text-xs text-primary font-mono animate-pulse truncate">{downloadProgress}</p>
              </div>
            )}

            {/* Footer buttons */}
            <div className="px-6 py-4 border-t border-border flex items-center justify-between gap-3">
              <span className="text-xs text-muted-foreground">
                Files save to your device&apos;s Downloads folder
              </span>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  className="border border-primary/60"
                  onClick={() => !isDownloading && setDownloadsOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  className="border border-primary/60 gap-2"
                  disabled={selectedIds.size === 0 || isDownloading}
                  isLoading={isDownloading}
                  onClick={handleExportZip}
                >
                  <FolderDown className="w-4 h-4" />
                  Export Forensic Zip
                </Button>
                <Button
                  variant="ghost"
                  className="bg-secondary/40 border border-border gap-2"
                  disabled={selectedIds.size === 0 || isDownloading}
                  isLoading={isDownloading}
                  onClick={handleDownloadSelected}
                >
                  <Download className="w-4 h-4" />
                  Files Only
                </Button>
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* ========== CONFIRM DELETE MODAL ========== */}
      <Modal
        isOpen={!!confirmDeleteId}
        onClose={() => !isDeleting && setConfirmDeleteId(null)}
        title="Delete Scan"
      >
        <div className="space-y-5">
          <p className="text-sm text-muted-foreground leading-relaxed">
            Are you sure you want to <span className="text-destructive font-semibold">delete this scan</span>?
            This action cannot be undone.
          </p>
          <div className="flex gap-3 justify-end">
            <Button variant="ghost" className="border border-primary/60" onClick={() => setConfirmDeleteId(null)}>
              Cancel
            </Button>
            <Button variant="danger" className="border border-primary/60" isLoading={isDeleting} onClick={doDelete}>
              Delete
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
