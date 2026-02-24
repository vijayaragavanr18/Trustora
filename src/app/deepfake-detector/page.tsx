"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { UploadZone } from '@/components/UploadZone';
import { Navbar } from '@/components/Navbar';
import { api } from '@/lib/api';

export default function DeepfakeDetectorPage() {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Proper auth check
    if (typeof window !== 'undefined') {
      if (!api.isAuthenticated()) {
        router.push('/login');
      } else {
        setIsChecking(false);
      }
    }
  }, [router]);

  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
          <p className="text-muted-foreground">Checking authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background bg-grid bg-radial-fade">
      <Navbar />
      <main className="container mx-auto px-6 py-8 max-w-4xl">
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold mb-4 font-display">Deepfake Detection</h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload an image or video to analyze for deepfake manipulation using our advanced AI models.
          </p>
        </div>

        <div className="bg-card border border-border rounded-xl p-8 shadow-sm">
          <UploadZone
            acceptedTypes={['image/jpeg', 'image/png', 'video/mp4', 'video/quicktime']}
            maxSize={100}
          />
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
            <div className="text-3xl mb-2">📸</div>
            <h3 className="font-semibold mb-1">Image Analysis</h3>
            <p className="text-sm text-muted-foreground">Detects GAN artifacts and face swapping in photos.</p>
          </div>
          <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
            <div className="text-3xl mb-2">🎥</div>
            <h3 className="font-semibold mb-1">Video Analysis</h3>
            <p className="text-sm text-muted-foreground">Frame-by-frame analysis for temporal inconsistencies.</p>
          </div>
          <div className="p-4 rounded-lg bg-secondary/30 border border-border/50">
            <div className="text-3xl mb-2">🔊</div>
            <h3 className="font-semibold mb-1">Audio Analysis</h3>
            <p className="text-sm text-muted-foreground">Identify voice cloning and synthetic speech.</p>
          </div>
        </div>
      </main>
    </div>
  );
}