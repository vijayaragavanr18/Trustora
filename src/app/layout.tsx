import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Trustora AI — Deepfake Detection & Media Forensics",
  description:
    "Enterprise-grade media integrity analysis powered by advanced neural networks. Detect deepfakes and protect truth.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
