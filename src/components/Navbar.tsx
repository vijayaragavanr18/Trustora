"use client";

import { Shield, Bell, User } from "lucide-react";
import { motion } from "framer-motion";
import Link from "next/link";

const navItems = ["Dashboard", "Analyze", "Reports", "Threat Intel"];

export function Navbar() {
  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="border-b border-border bg-card/80 backdrop-blur-md sticky top-0 z-50"
    >
      <div className="container mx-auto flex items-center justify-between h-16 px-6">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3">
          <div className="rounded-md bg-primary/10 p-1.5 glow-border">
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <span className="font-display text-xl font-bold tracking-tight text-foreground">
            Trustora
          </span>
          <span className="hidden sm:inline-block text-xs font-mono text-muted-foreground ml-2 px-2 py-0.5 rounded border border-border bg-secondary">
            v2.4.1
          </span>
        </Link>

        {/* Nav links */}
        <nav className="hidden md:flex items-center gap-1 text-sm">
          {navItems.map((item, i) => (
            <button
              key={item}
              className={`px-3.5 py-2 rounded-md font-medium transition-colors ${
                i === 0
                  ? "text-primary bg-primary/10"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary"
              }`}
            >
              {item}
            </button>
          ))}
        </nav>

        {/* Actions */}
        <div className="flex items-center gap-2">
          <button className="relative p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors">
            <Bell className="h-[18px] w-[18px]" />
            <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-threat-high" />
          </button>
          <button className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors">
            <User className="h-[18px] w-[18px]" />
          </button>
        </div>
      </div>
    </motion.header>
  );
}
