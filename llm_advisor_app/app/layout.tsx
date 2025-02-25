"use client";

import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider, useAuth } from "@/hooks/auth";
import Navbar from "@/components/navigation/NavBar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// We can't use metadata with a client component, so we'll define it elsewhere
// or use a different approach for page titles

function LayoutContent({ children }: Readonly<{ children: React.ReactNode }>) {
  const { user } = useAuth();

  return (
    <div className="flex flex-col min-h-screen">
      {user && <Navbar />}
      <main
        className={`flex-1 container mx-auto px-4 py-6 ${!user ? "pt-0" : ""}`}
      >
        {children}
      </main>
    </div>
  );
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <AuthProvider>
          <LayoutContent>{children}</LayoutContent>
        </AuthProvider>
      </body>
    </html>
  );
}
