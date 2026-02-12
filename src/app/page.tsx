import { Navbar } from "@/components/Navbar";
import { HeroSection } from "@/components/HeroSection";
import { StatsGrid } from "@/components/StatsGrid";
import { UploadZone } from "@/components/UploadZone";
import { RecentScans } from "@/components/RecentScans";
import { ThreatMap } from "@/components/ThreatMap";

export default function Home() {
  return (
    <div className="min-h-screen bg-background bg-grid bg-radial-fade">
      <Navbar />
      <main className="container mx-auto px-6 py-8 max-w-7xl">
        <HeroSection />
        <StatsGrid />
        <div className="mt-8">
          <UploadZone />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          <div className="lg:col-span-2">
            <RecentScans />
          </div>
          <div>
            <ThreatMap />
          </div>
        </div>
      </main>
    </div>
  );
}
