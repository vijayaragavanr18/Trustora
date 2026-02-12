"use client";

import { motion } from "framer-motion";
import { ShieldCheck, ArrowRight } from "lucide-react";

export function HeroSection() {
  return (
    <section className="relative overflow-hidden rounded-xl border border-border mb-8">
      {/* Gradient background instead of image */}
      <div className="absolute inset-0">
        <div className="w-full h-full bg-gradient-to-br from-primary/20 via-background to-background opacity-60" />
        <div className="absolute inset-0 bg-gradient-to-r from-background via-background/90 to-background/60" />
      </div>

      <div className="relative px-8 py-14 md:py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="max-w-2xl"
        >
          <div className="flex items-center gap-2 mb-4">
            <ShieldCheck className="h-5 w-5 text-primary" />
            <span className="text-xs font-mono uppercase tracking-widest text-primary">
              AI-Powered Forensic Analysis
            </span>
          </div>
          <h1 className="font-display text-4xl md:text-5xl font-bold text-foreground leading-tight mb-4">
            Detect Deepfakes.{" "}
            <span className="text-gradient-primary">Protect Truth.</span>
          </h1>
          <p className="text-muted-foreground text-lg leading-relaxed mb-8 max-w-lg">
            Enterprise-grade media integrity analysis powered by advanced neural
            networks. Identify manipulated content before it causes damage.
          </p>
          <div className="flex flex-wrap gap-3">
            <button className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary text-primary-foreground font-semibold text-sm hover:opacity-90 transition-opacity glow-primary">
              Start Analysis
              <ArrowRight className="h-4 w-4" />
            </button>
            <button className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-border text-foreground font-semibold text-sm hover:bg-secondary transition-colors">
              View Demo
            </button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
