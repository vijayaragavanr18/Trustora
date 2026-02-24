"use client";

import { motion } from "framer-motion";

interface SkeletonProps {
  className?: string;
  count?: number;
}

export function Skeleton({ className = "", count = 1 }: SkeletonProps) {
  return (
    <>
      {Array(count).fill(0).map((_, i) => (
        <motion.div
           key={i}
           initial={{ opacity: 0.5 }}
           animate={{ opacity: 0.8 }}
           transition={{ duration: 1, repeat: Infinity, repeatType: "reverse" }}
           className={`bg-zinc-800 rounded-md ${className}`}
        />
      ))}
    </>
  );
}
