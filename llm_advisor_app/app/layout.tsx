"use client";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider, useAuth } from "@/hooks/auth";
import Navbar from "@/components/navigation/NavBar";
import { Suspense } from "react";
import Loading from "@/components/ui/loading";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Layout content with authentication awareness
function LayoutContent({ children }: Readonly<{ children: React.ReactNode }>) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="flex flex-col min-h-screen">
      {isAuthenticated && <Navbar />}
      <main
        className={`flex-1 container mx-auto px-4 py-6 ${
          !isAuthenticated ? "pt-0" : ""
        }`}
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
          <Suspense fallback={<Loading />}>
            <LayoutContent>{children}</LayoutContent>
          </Suspense>
        </AuthProvider>
      </body>
    </html>
  );
}
