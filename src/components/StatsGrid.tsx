"use client";

import { Shield, ShieldCheck, Activity, Eye, LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface Stat {
  label: string;
  value: string;
  icon: LucideIcon;
  change: string;
}

const stats: Stat[] = [
  { label: "Scans Today", value: "1,247", icon: Eye, change: "+12%" },
  { label: "Threats Detected", value: "38", icon: Shield, change: "+3" },
  { label: "Accuracy Rate", value: "99.7%", icon: ShieldCheck, change: "±0.1%" },
  { label: "Active Monitors", value: "156", icon: Activity, change: "+8" },
];

export function StatsGrid() {
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
              <Icon className="h-4 w-4 text-primary" />
            </div>
            <div className="text-3xl font-display font-bold text-foreground">
              {stat.value}
            </div>
            <span className="text-xs font-mono text-primary mt-1 inline-block">
              {stat.change}
            </span>
          </motion.div>
        );
      })}
    </div>
  );
}
