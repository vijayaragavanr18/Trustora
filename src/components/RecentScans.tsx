import { AlertTriangle, CheckCircle, Clock, FileSearch } from "lucide-react";
import { motion } from "framer-motion";

const recentScans = [
  {
    id: 1,
    filename: "press_photo_042.jpg",
    type: "Image",
    status: "Threat Detected",
    level: "high" as const,
    confidence: 94.2,
    timestamp: "2 min ago",
  },
  {
    id: 2,
    filename: "interview_clip.mp4",
    type: "Video",
    status: "Clean",
    level: "low" as const,
    confidence: 99.1,
    timestamp: "8 min ago",
  },
  {
    id: 3,
    filename: "social_media_post.png",
    type: "Image",
    status: "Suspicious",
    level: "medium" as const,
    confidence: 67.8,
    timestamp: "15 min ago",
  },
  {
    id: 4,
    filename: "quarterly_report.jpg",
    type: "Image",
    status: "Clean",
    level: "low" as const,
    confidence: 98.5,
    timestamp: "22 min ago",
  },
  {
    id: 5,
    filename: "video_statement.mp4",
    type: "Video",
    status: "Analyzing",
    level: "medium" as const,
    confidence: 0,
    timestamp: "Just now",
  },
];

const levelColors = {
  high: "text-threat-high",
  medium: "text-threat-medium",
  low: "text-threat-low",
};

const levelBg = {
  high: "bg-threat-high/10",
  medium: "bg-threat-medium/10",
  low: "bg-threat-low/10",
};

const statusIcons = {
  "Threat Detected": AlertTriangle,
  Clean: CheckCircle,
  Suspicious: FileSearch,
  Analyzing: Clock,
};

export function RecentScans() {
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
        <span className="text-xs font-mono text-muted-foreground">
          LIVE FEED
          <span className="inline-block ml-1.5 h-1.5 w-1.5 rounded-full bg-primary animate-pulse-glow" />
        </span>
      </div>
      <div className="divide-y divide-border">
        {recentScans.map((scan) => {
          const Icon = statusIcons[scan.status as keyof typeof statusIcons] || FileSearch;
          return (
            <div
              key={scan.id}
              className="flex items-center justify-between px-5 py-3.5 hover:bg-secondary/50 transition-colors"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className={`rounded p-1.5 ${levelBg[scan.level]}`}>
                  <Icon className={`h-4 w-4 ${levelColors[scan.level]}`} />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-mono text-foreground truncate">
                    {scan.filename}
                  </p>
                  <p className="text-xs text-muted-foreground">{scan.type}</p>
                </div>
              </div>
              <div className="flex items-center gap-6 text-right shrink-0">
                <div>
                  <p className={`text-xs font-semibold ${levelColors[scan.level]}`}>
                    {scan.status}
                  </p>
                  {scan.confidence > 0 && (
                    <p className="text-xs font-mono text-muted-foreground">
                      {scan.confidence}% conf.
                    </p>
                  )}
                </div>
                <span className="text-xs text-muted-foreground w-16 text-right">
                  {scan.timestamp}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
