import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StartUSBusiness — Start Your US Business From Anywhere",
  description:
    "AI-powered USA business setup for founders from UAE, Pakistan, India and worldwide. Wyoming LLC formation, EIN assistance, registered agent, US address, and banking application support.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-body">{children}</body>
    </html>
  );
}
