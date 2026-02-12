import { Upload, FileImage, FileVideo } from "lucide-react";
import { motion } from "framer-motion";
import { useState, useCallback } from "react";

export function UploadZone() {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4, duration: 0.5 }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`relative rounded-lg border-2 border-dashed p-10 text-center transition-all duration-300 cursor-pointer group ${
        isDragging
          ? "border-primary bg-primary/5 glow-primary"
          : "border-border hover:border-primary/50 bg-card"
      }`}
    >
      {/* Scan line effect */}
      <div className="absolute inset-0 overflow-hidden rounded-lg pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity">
        <div className="absolute inset-x-0 h-px scan-line animate-scan" />
      </div>

      <div className="flex flex-col items-center gap-4">
        <div className="rounded-full bg-secondary p-4">
          <Upload className="h-8 w-8 text-primary" />
        </div>
        <div>
          <h3 className="font-display text-lg font-semibold text-foreground mb-1">
            Upload Media for Analysis
          </h3>
          <p className="text-sm text-muted-foreground max-w-md mx-auto">
            Drag and drop images or videos to scan for deepfake manipulation, 
            AI-generated content, and forensic anomalies.
          </p>
        </div>
        <div className="flex items-center gap-6 text-xs font-mono text-muted-foreground mt-2">
          <span className="flex items-center gap-1.5">
            <FileImage className="h-3.5 w-3.5" /> JPG, PNG, WEBP
          </span>
          <span className="flex items-center gap-1.5">
            <FileVideo className="h-3.5 w-3.5" /> MP4, MOV, AVI
          </span>
        </div>
      </div>
    </motion.div>
  );
}
