import { motion } from "framer-motion";

export function ThreatMap() {
  const threats = [
    { label: "GAN-Generated", pct: 42 },
    { label: "Face Swap", pct: 28 },
    { label: "Voice Clone", pct: 15 },
    { label: "Metadata Tampering", pct: 10 },
    { label: "Other", pct: 5 },
  ];

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
              <span className="font-mono text-xs text-muted-foreground">{t.pct}%</span>
            </div>
            <div className="h-2 rounded-full bg-secondary overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${t.pct}%` }}
                transition={{ delay: 0.8 + i * 0.1, duration: 0.8, ease: "easeOut" }}
                className="h-full rounded-full bg-primary"
                style={{
                  opacity: 1 - i * 0.15,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
