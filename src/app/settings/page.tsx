"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { User, Bell, Shield, X, Check, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { Modal } from "@/components/Modal";
import { Button } from "@/components/ui/Button";

export default function SettingsPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [preferences, setPreferences] = useState<any>({
    analysis_complete: true,
    security_alerts: true,
    marketing: false
  });

  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState("");
  const [modalValue, setModalValue] = useState("");
  const [editingField, setEditingField] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const userData = await api.getMe();
        setUser(userData);
        if (userData.preferences) {
          try {
            setPreferences(JSON.parse(userData.preferences));
          } catch (e) {
            console.error("Failed to parse preferences", e);
          }
        }
      } catch (error) {
        console.error("Failed to fetch user", error);
        toast.error("Failed to load settings");
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, []);

  const handleUpdate = async (updateData: any) => {
    try {
      setSaving(true);
      const updatedUser = await api.updateMe(updateData);
      setUser(updatedUser);
      toast.success("Settings updated");
      setModalOpen(false);
    } catch (error) {
      console.error("Update failed", error);
      toast.error("Failed to update settings");
    } finally {
      setSaving(false);
    }
  };

  const openEditModal = (field: string, title: string, initialValue: string) => {
    setEditingField(field);
    setModalTitle(title);
    setModalValue(initialValue);
    setModalOpen(true);
  };

  const handleModalSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingField === "delete") {
      confirmDelete();
    } else {
      handleUpdate({ [editingField]: modalValue });
    }
  };

  const togglePreference = async (key: string) => {
    const newPrefs = { ...preferences, [key]: !preferences[key] };
    setPreferences(newPrefs);
    await handleUpdate({ preferences: JSON.stringify(newPrefs) });
  };

  const confirmDelete = async () => {
    try {
      setSaving(true);
      await api.deleteMe();
      toast.success("Account deleted");
      api.logout();
    } catch (error) {
      toast.error("Failed to delete account");
    } finally {
      setSaving(false);
      setModalOpen(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background bg-grid bg-radial-fade">
      <Navbar />
      <main className="container mx-auto px-6 py-12 max-w-4xl">
        <div className="flex items-center justify-between mb-8">
            <h1 className="font-display text-3xl font-bold text-foreground">
            Settings
            </h1>
            {saving && <div className="flex items-center gap-2 text-sm text-muted-foreground animate-pulse">
                <Loader2 className="w-3 h-3 animate-spin" /> Saving...
            </div>}
        </div>

        <div className="space-y-8">
          {/* Account Preferences */}
          <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-border bg-secondary/30 flex items-center gap-3">
              <User className="w-5 h-5 text-primary" />
              <h2 className="font-semibold text-foreground">Account Preferences</h2>
            </div>
            <div className="divide-y divide-border/50">
              <div className="px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-foreground">Full Name</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{user?.full_name || "Not set"}</p>
                </div>
                <button 
                    onClick={() => openEditModal("full_name", "Update Full Name", user?.full_name || "")}
                    className="text-sm text-primary hover:underline font-medium"
                >
                  Edit
                </button>
              </div>
              <div className="px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-foreground">Organization</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{user?.organization || "Not set"}</p>
                </div>
                <button 
                  onClick={() => openEditModal("organization", "Update Organization", user?.organization || "")}
                  className="text-sm text-primary hover:underline font-medium"
                >
                  Edit
                </button>
              </div>
              <div className="px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-foreground">Language</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{user?.language || "English (US)"}</p>
                </div>
                <select 
                    className="bg-background border border-border rounded text-xs p-1"
                    value={user?.language || "English (US)"}
                    onChange={(e) => handleUpdate({ language: e.target.value })}
                >
                    <option>English (US)</option>
                    <option>Tamil</option>
                    <option>Hindi</option>
                    <option>Spanish</option>
                </select>
              </div>
            </div>
          </div>

          {/* Security */}
          <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-border bg-secondary/30 flex items-center gap-3">
              <Shield className="w-5 h-5 text-primary" />
              <h2 className="font-semibold text-foreground">Security & Access</h2>
            </div>
            <div className="divide-y divide-border/50">
              <div className="px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-foreground">Email Address</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">{user?.email}</p>
                </div>
                <span className="text-xs text-muted-foreground bg-secondary px-2 py-0.5 rounded">Primary</span>
              </div>
              <div className="px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-foreground">Change Password</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">Last updated 3 months ago</p>
                </div>
                <button 
                    onClick={() => openEditModal("password", "Update Password", "")}
                    className="text-sm text-primary hover:underline font-medium"
                >
                  Update
                </button>
              </div>
            </div>
          </div>

          {/* Notifications */}
          <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-border bg-secondary/30 flex items-center gap-3">
              <Bell className="w-5 h-5 text-primary" />
              <h2 className="font-semibold text-foreground">Notifications</h2>
            </div>
            <div className="divide-y divide-border/50">
               <div className="px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-foreground">Analysis Complete</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">Email me when a scan finishes</p>
                </div>
                <button 
                    onClick={() => togglePreference('analysis_complete')}
                    className={`w-11 h-6 rounded-full transition-colors relative ${preferences.analysis_complete ? 'bg-primary' : 'bg-secondary border border-border'}`}
                >
                  <div className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${preferences.analysis_complete ? 'translate-x-5' : 'translate-x-0'}`} />
                </button>
              </div>
              <div className="px-6 py-4 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-medium text-foreground">Security Alerts</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">Notify me of suspicious account activity</p>
                </div>
                <button 
                    onClick={() => togglePreference('security_alerts')}
                    className={`w-11 h-6 rounded-full transition-colors relative ${preferences.security_alerts ? 'bg-primary' : 'bg-secondary border border-border'}`}
                >
                  <div className={`absolute top-1 left-1 bg-white w-4 h-4 rounded-full transition-transform ${preferences.security_alerts ? 'translate-x-5' : 'translate-x-0'}`} />
                </button>
              </div>
            </div>
          </div>

          {/* Danger Zone */}
          <div className="bg-destructive/5 border border-destructive/20 rounded-xl p-6">
            <h3 className="font-semibold text-destructive mb-2">Danger Zone</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Permanently delete your account and all associated analysis data.
            </p>
            <button 
                onClick={() => openEditModal("delete", "Delete Account", "")}
                className="px-4 py-2 bg-destructive text-destructive-foreground rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
            >
              Delete Account
            </button>
          </div>
        </div>
      </main>

      {/* Modern Modal Replacement for Prompt */}
      <Modal 
        isOpen={modalOpen} 
        onClose={() => setModalOpen(false)} 
        title={modalTitle}
      >
        <form onSubmit={handleModalSubmit} className="space-y-4">
          {editingField === "delete" ? (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                This action is irreversible. All your scan history, reports, and evidence will be lost forever.
              </p>
              <div className="flex gap-3 justify-end mt-6">
                <Button variant="ghost" type="button" onClick={() => setModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="danger" type="submit" isLoading={saving}>
                  Yes, Delete My Account
                </Button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">
                  New Value
                </label>
                <input 
                  type={editingField === "password" ? "password" : "text"}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                  value={modalValue}
                  onChange={(e) => setModalValue(e.target.value)}
                  autoFocus
                  placeholder={`Enter new ${modalTitle.toLowerCase().replace('update ', '')}...`}
                />
              </div>
              <div className="flex gap-3 justify-end mt-6">
                <Button variant="ghost" type="button" onClick={() => setModalOpen(false)}>
                  Cancel
                </Button>
                <Button variant="primary" type="submit" isLoading={saving}>
                  Save Changes
                </Button>
              </div>
            </div>
          )}
        </form>
      </Modal>
    </div>
  );
}
