"use client";
import { useState } from "react";
import { useAuth } from "@/hooks/auth";
import { env } from "@/environment";
import AuthComponent from "@/components/auth/AuthComponent";
import UserProfile from "@/components/user/UserProfile";
import StudentManager from "@/components/database_interaction";
import FancyTitle from "@/components/styling/FancyTitle";

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const { user, getToken } = useAuth();
  const apiUrl = env.apiUrl;

  const handleAuthStateChange = (loggedIn: boolean) => {
    setIsLoggedIn(loggedIn);
  };

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <AuthComponent onAuthStateChange={handleAuthStateChange} />

      {user && isLoggedIn && <FancyTitle />}
    </div>
  );
}
