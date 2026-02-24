"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle, Clock, FileSearch, LucideIcon } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";
import { formatDistanceToNow } from 'date-fns';
import { useRouter } from "next/navigation";

interface Scan {
  id: string;
  file_name: string;
  file_type: string;
  status: string;
  risk_level: string;
  confidence: number;
  created_at: string;
  deepfake_score?: number;
}

export function RecentScans() {
  const router = useRouter();
  const [scans, setScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        if (api.isAuthenticated()) {
          const data = await api.getHistory();
          setScans(data.slice(0, 5)); // Show only last 5
        }
      } catch (error) {
        console.error("Failed to fetch history:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
    // Poll every 5 seconds for live updates
    const interval = setInterval(fetchHistory, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string, risk: string): LucideIcon => {
    if (status === 'pending' || status === 'processing') return Clock;
    if (risk === 'high') return AlertTriangle;
    if (risk === 'medium') return FileSearch;
    return CheckCircle;
  };

  const getLevelColor = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'high': return 'text-red-500';
      case 'medium': return 'text-yellow-500';
      case 'low': return 'text-green-500';
      default: return 'text-muted-foreground';
    }
  };

  const getLevelBg = (risk: string) => {
    switch (risk?.toLowerCase()) {
      case 'high': return 'bg-red-500/10';
      case 'medium': return 'bg-yellow-500/10';
      case 'low': return 'bg-green-500/10';
      default: return 'bg-secondary';
    }
  };

  if (loading && scans.length === 0) {
    return (
      <div className="rounded-lg border border-border bg-card p-8 text-center text-muted-foreground">
        Loading recent scans...
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.6, duration: 0.5 }}
      className="rounded-lg border border-border bg-card"
    >
      <div className="p-5 border-b border-border flex items-center justify-between">
        <h2 className="font-display text-lg font-semibold text-foreground">
          Recent Scans
        </h2>
        <span className="text-xs font-mono text-muted-foreground flex items-center gap-2">
          LIVE FEED
          <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
        </span>
      </div>
      
      {scans.length === 0 ? (
        <div className="p-8 text-center text-muted-foreground text-sm">
          No scans yet. Upload a file to see it here!
        </div>
      ) : (
        <div className="divide-y divide-border">
          {scans.map((scan) => {
            const Icon = getStatusIcon(scan.status, scan.risk_level);
            const riskColor = getLevelColor(scan.risk_level);
            const riskBg = getLevelBg(scan.risk_level);
            
            return (
              <div
                key={scan.id}
                className="flex items-center justify-between px-5 py-3.5 hover:bg-secondary/50 transition-colors"
                onClick={() => router.push(`/analysis/${scan.id}`)}
                onKeyDown={(e) => e.key === 'Enter' && router.push(`/analysis/${scan.id}`)}
                role="button"
                tabIndex={0}
                aria-label={`View analysis for ${scan.file_name}`}
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className={`rounded p-1.5 ${riskBg}`}>
                    <Icon className={`h-4 w-4 ${riskColor}`} />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-mono text-foreground truncate max-w-[150px]" title={scan.file_name}>
                      {scan.file_name}
                    </p>
                    <p className="text-xs text-muted-foreground capitalize">{scan.file_type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-6 text-right shrink-0">
                  <div>
                    <p className={`text-xs font-semibold ${riskColor} capitalize`}>
                      {scan.status === 'completed' ? (scan.risk_level || 'Safe') : scan.status}
                    </p>
                    {(scan.confidence !== undefined && scan.confidence !== null) ? (
                      <p className="text-xs font-mono text-muted-foreground">
                        {scan.confidence.toFixed(1)}% conf.
                      </p>
                    ) : null}
                  </div>
                  <span suppressHydrationWarning className="text-xs text-muted-foreground w-20 text-right">
                    {formatDistanceToNow(new Date(scan.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}
