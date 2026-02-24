"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { api } from "@/lib/api";

interface ThreatType {
  label: string;
  pct: number;
}

export function ThreatMap() {
  const [threats, setThreats] = useState<ThreatType[]>([
    { label: "AI Generative", pct: 0 },
    { label: "Face Inconsistency", pct: 0 },
    { label: "Audio Cloned", pct: 0 },
    { label: "Metadata Missing", pct: 0 },
    { label: "Safe / Other", pct: 100 },
  ]);

  useEffect(() => {
    const fetchThreatData = async () => {
      try {
        if (!api.isAuthenticated()) return;
        const history = await api.getHistory();
        const completed = history.filter((s: any) => s.status === "completed");
        
        if (completed.length === 0) return;

        let aiCount = 0;
        let faceCount = 0;
        let audioCount = 0;
        let metaCount = 0;
        let totalArtifacts = 0;

        completed.forEach((scan: any) => {
          const artifacts = scan.artifacts_found || [];
          if (artifacts.includes("ai_deepfake_detected")) aiCount++;
          if (artifacts.includes("face_boundary_mismatch")) faceCount++;
          if (artifacts.includes("low_mfcc_variation") || artifacts.includes("pitch_irregularity")) audioCount++;
          if (artifacts.includes("missing_exif_data") || artifacts.includes("editing_software_detected")) metaCount++;
        });

        const total = completed.length;
        const safeCount = completed.filter((s: any) => s.risk_level === "LOW").length;

        setThreats([
          { label: "AI Generative", pct: Math.round((aiCount / total) * 100) },
          { label: "Face Inconsistency", pct: Math.round((faceCount / total) * 100) },
          { label: "Audio Cloned", pct: Math.round((audioCount / total) * 100) },
          { label: "Metadata Missing", pct: Math.round((metaCount / total) * 100) },
          { label: "Safe Content", pct: Math.round((safeCount / total) * 100) },
        ]);
      } catch (err) {
        // Fallback or do nothing
      }
    };

    fetchThreatData();
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.7, duration: 0.5 }}
      className="rounded-lg border border-border bg-card p-5"
    >
      <h2 className="font-display text-lg font-semibold text-foreground mb-5">
        Threat Distribution
      </h2>
      <div className="space-y-4">
        {threats.map((t, i) => (
          <div key={t.label}>
            <div className="flex justify-between text-sm mb-1.5">
              <span className="text-secondary-foreground">{t.label}</span>
              <span className="font-mono text-xs text-muted-foreground">
                {t.pct}%
              </span>
            </div>
            <div className="h-2 rounded-full bg-secondary overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${t.pct}%` }}
                transition={{
                  delay: 0.8 + i * 0.1,
                  duration: 0.8,
                  ease: "easeOut",
                }}
                className={`h-full rounded-full ${
                  t.label === "Safe Content" ? "bg-green-500" : "bg-primary"
                }`}
                style={{ opacity: 1 - i * 0.1 }}
              />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
