"use client";

import { useEffect, useState } from "react";
import { Shield, ShieldCheck, Activity, Eye, LucideIcon } from "lucide-react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";

interface Stat {
  label: string;
  value: string;
  icon: LucideIcon;
  change: string;
  color: string;
}

export function StatsGrid() {
  const [stats, setStats] = useState<Stat[]>([
    { label: "Total Scans", value: "—", icon: Eye, change: "Loading...", color: "text-primary" },
    { label: "Threats Detected", value: "—", icon: Shield, change: "Loading...", color: "text-red-400" },
    { label: "Avg. Confidence", value: "—", icon: ShieldCheck, change: "Loading...", color: "text-green-400" },
    { label: "Safe Files", value: "—", icon: Activity, change: "Loading...", color: "text-cyan-400" },
  ]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        if (!api.isAuthenticated()) return;
        const history = await api.getHistory();

        const total = history.length;
        const completed = history.filter((s: any) => s.status === "completed");
        const threats = completed.filter(
          (s: any) => s.risk_level === "HIGH" || s.risk_level === "CRITICAL"
        ).length;
        const safe = completed.filter(
          (s: any) => s.risk_level === "LOW"
        ).length;

        const avgConf =
          completed.length > 0
            ? completed.reduce((sum: number, s: any) => sum + (s.confidence || 0), 0) /
              completed.length
            : 0;

        // Today's scans
        const today = new Date().toDateString();
        const todayScans = history.filter(
          (s: any) => new Date(s.created_at).toDateString() === today
        ).length;

        setStats([
          {
            label: "Total Scans",
            value: total.toString(),
            icon: Eye,
            change: `${todayScans} today`,
            color: "text-primary",
          },
          {
            label: "Threats Detected",
            value: threats.toString(),
            icon: Shield,
            change: total > 0 ? `${((threats / total) * 100).toFixed(1)}% threat rate` : "—",
            color: "text-red-400",
          },
          {
            label: "Avg. Confidence",
            value: avgConf > 0 ? `${avgConf.toFixed(1)}%` : "—",
            icon: ShieldCheck,
            change: `${completed.length} analyzed`,
            color: "text-green-400",
          },
          {
            label: "Safe Files",
            value: safe.toString(),
            icon: Activity,
            change: total > 0 ? `${((safe / total) * 100).toFixed(1)}% clean` : "—",
            color: "text-cyan-400",
          },
        ]);
      } catch (err) {
        // Keep default dashes if not logged in / API down
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.5 }}
            className="rounded-lg border border-border bg-card p-5 glow-border"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                {stat.label}
              </span>
              <Icon className={`h-4 w-4 ${stat.color}`} />
            </div>
            <div className="text-3xl font-display font-bold text-foreground">
              {stat.value}
            </div>
            <span className={`text-xs font-mono mt-1 inline-block ${stat.color}`}>
              {stat.change}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
