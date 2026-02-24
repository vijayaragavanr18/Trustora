"use client";

import { Shield, User, Settings, LogOut, History, LogIn, Menu, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { api } from "@/lib/api";

const navItems = ["Dashboard", "Deepfake Detector", "Digital Evidence", "History"];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [user, setUser] = useState<{ full_name: string; email: string } | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      if (api.isAuthenticated()) {
        try {
          const userData = await api.getMe();
          setUser(userData);
        } catch (error) {
          console.error("Failed to fetch user:", error);
        }
      }
    };
    fetchUser();
  }, [pathname]); // Re-fetch on path change to keep auth state fresh

  const handleLogout = () => {
    api.logout();
    setIsUserMenuOpen(false);
  };

  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="border-b border-border bg-card/80 backdrop-blur-md sticky top-0 z-50"
    >
      <div className="container mx-auto flex items-center justify-between h-16 px-6 relative">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 shrink-0">
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

        {/* Right Side Container (Desktop) */}
        <div className="hidden md:flex items-center gap-6">
          {/* Nav links */}
          <nav className="flex items-center gap-1 text-sm">
            {navItems.map((item) => {
              const href =
                item === "Dashboard"
                  ? "/"
                  : item === "Deepfake Detector"
                  ? "/deepfake-detector"
                  : item === "Digital Evidence"
                  ? "/digital-evidence"
                  : "/history";
              const isActive = pathname === href;

              return (
                <Link
                  key={item}
                  href={href}
                  className={`px-3.5 py-2 rounded-md font-medium transition-colors ${
                    isActive
                      ? "text-primary bg-primary/10"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                  }`}
                >
                  {item}
                </Link>
              );
            })}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-2 pl-2 border-l border-border/40">
            <div className="relative">
              <button 
                onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                suppressHydrationWarning
                className={`p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors ${isUserMenuOpen ? 'bg-secondary text-foreground' : ''}`}
              >
                <User className="h-[18px] w-[18px]" />
              </button>

              <AnimatePresence>
                {isUserMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 10, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: 10, scale: 0.95 }}
                    transition={{ duration: 0.1 }}
                    className="absolute right-0 top-full mt-2 w-56 rounded-xl border border-border bg-card shadow-lg p-2 z-50 origin-top-right"
                  >
                    <div className="px-3 py-2 border-b border-border/50 mb-1">
                      <p className="text-sm font-medium text-foreground">{user?.full_name || "Guest"}</p>
                      <p className="text-xs text-muted-foreground truncate">{user?.email || "Not signed in"}</p>
                    </div>
                    
                    <Link 
                      href="/settings"
                      onClick={() => setIsUserMenuOpen(false)}
                      className="flex items-center gap-2 px-3 py-2 text-sm text-foreground rounded-lg hover:bg-secondary transition-colors"
                    >
                      <Settings className="w-4 h-4" />
                      Settings
                    </Link>



                    <div className="border-t border-border/50 my-1 pt-1">
                      {user ? (
                        <button
                            onClick={handleLogout}
                            className="w-full flex items-center gap-2 px-3 py-2 text-sm text-foreground rounded-lg hover:bg-secondary transition-colors text-left"
                        >
                            <LogOut className="w-4 h-4" />
                            Sign Out
                        </button>
                      ) : (
                        <Link 
                            href="/login"
                            onClick={() => setIsUserMenuOpen(false)}
                            className="flex items-center gap-2 px-3 py-2 text-sm text-foreground rounded-lg hover:bg-secondary transition-colors"
                        >
                            <LogIn className="w-4 h-4" />
                            Sign In
                        </Link>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Mobile Menu Toggle */}
        <div className="md:hidden flex items-center gap-4">
            <button 
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                suppressHydrationWarning
                className="p-2 text-foreground"
            >
                {isMobileMenuOpen ? <X /> : <Menu />}
            </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && (
            <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="md:hidden border-t border-border bg-card overflow-hidden"
            >
                <nav className="flex flex-col p-4 gap-2">
                    {navItems.map((item) => {
                        const href =
                            item === "Dashboard"
                            ? "/"
                            : item === "Deepfake Detector"
                            ? "/deepfake-detector"
                            : item === "Digital Evidence"
                            ? "/digital-evidence"
                            : "/history";
                        const isActive = pathname === href;
                        return (
                            <Link
                                key={item}
                                href={href}
                                onClick={() => setIsMobileMenuOpen(false)}
                                className={`px-4 py-3 rounded-lg font-medium transition-colors ${
                                isActive
                                    ? "text-primary bg-primary/10"
                                    : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                                }`}
                            >
                                {item}
                            </Link>
                        );
                    })}
                     <div className="h-px bg-border my-2" />
                     <div className="px-4 py-2">
                        <p className="text-sm font-medium text-foreground">{user?.full_name || "Guest"}</p>
                        <p className="text-xs text-muted-foreground">{user?.email || "Not signed in"}</p>
                     </div>
                     <Link
                        href="/settings"
                        onClick={() => setIsMobileMenuOpen(false)}
                        className="px-4 py-3 rounded-lg font-medium text-muted-foreground hover:text-foreground hover:bg-secondary flex gap-2"
                     >
                        <Settings className="w-5 h-5" /> Settings
                     </Link>
                     {user ? (
                        <button
                            onClick={() => {
                                handleLogout();
                                setIsMobileMenuOpen(false);
                            }}
                            className="px-4 py-3 rounded-lg font-medium text-destructive hover:bg-destructive/10 flex gap-2 text-left"
                        >
                            <LogOut className="w-5 h-5" /> Sign Out
                        </button>
                     ) : (
                        <Link
                            href="/login"
                            onClick={() => setIsMobileMenuOpen(false)}
                            className="px-4 py-3 rounded-lg font-medium text-muted-foreground hover:text-foreground hover:bg-secondary flex gap-2"
                        >
                            <LogIn className="w-5 h-5" /> Sign In
                        </Link>
                     )}
                </nav>
            </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
