"use client";
import { useState } from "react";
import { useAuth } from "@/hooks/auth";
import AuthComponent from "@/components/auth/AuthComponent";
import UserProfile from "@/components/user/UserProfileManager";

export default function Profile() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const { user } = useAuth();

  const handleAuthStateChange = (loggedIn: boolean) => {
    setIsLoggedIn(loggedIn);
  };

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <AuthComponent onAuthStateChange={handleAuthStateChange} />

      {user && isLoggedIn && <UserProfile />}
    </div>
  );
}
