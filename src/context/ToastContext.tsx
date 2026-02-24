"use client";

import { CheckCircle, AlertTriangle, AlertCircle, Info, X } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { createContext, useContext, useState, ReactNode } from "react";

type ToastType = "success" | "error" | "warning" | "info";

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  toast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const toast = (message: string, type: ToastType = "success") => {
    const id = Math.random().toString(36).substring(7);
    setToasts((prev) => [...prev, { id, message, type }]);
    
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95, transition: { duration: 0.2 } }}
              className={`
                pointer-events-auto flex items-center gap-3 min-w-[320px] p-4 rounded-xl border shadow-lg backdrop-blur-xl
                ${
                  t.type === "success"
                    ? "bg-green-500/10 border-green-500/20 text-green-500"
                    : t.type === "error"
                    ? "bg-red-500/10 border-red-500/20 text-red-500"
                    : t.type === "warning"
                    ? "bg-yellow-500/10 border-yellow-500/20 text-yellow-500"
                    : "bg-blue-500/10 border-blue-500/20 text-blue-500"
                }
              `}
            >
              {t.type === "success" && <CheckCircle className="w-5 h-5 shrink-0" />}
              {t.type === "error" && <AlertCircle className="w-5 h-5 shrink-0" />}
              {t.type === "warning" && <AlertTriangle className="w-5 h-5 shrink-0" />}
              {t.type === "info" && <Info className="w-5 h-5 shrink-0" />}
              
              <p className="flex-1 text-sm font-medium text-foreground">{t.message}</p>
              
              <button 
                onClick={() => removeToast(t.id)}
                className="opacity-70 hover:opacity-100 transition-opacity"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};
