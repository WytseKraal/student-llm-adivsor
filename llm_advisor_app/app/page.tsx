"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/auth";
import AuthComponent from "@/components/auth/AuthComponent";
import FancyTitle from "@/components/styling/FancyTitle";

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleAuthStateChange = (loggedIn: boolean) => {
    setIsLoggedIn(loggedIn);
  };

  // Only render auth-dependent content after component is mounted in the browser
  if (!isMounted) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        Loading...
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <AuthComponent onAuthStateChange={handleAuthStateChange} />
      {user && isLoggedIn && <FancyTitle />}
    </div>
  );
}
