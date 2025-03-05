"use client";
import { useState } from "react";
import { useAuth } from "@/hooks/auth";
import { env } from "@/environment";
import AuthComponent from "@/components/auth/AuthComponent";
import ChatService from "@/components/user/ChatService";

export default function Profile() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const { user, getToken } = useAuth();
  const apiUrl = env.apiUrl;

  const handleAuthStateChange = (loggedIn: boolean) => {
    setIsLoggedIn(loggedIn);
  };

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <AuthComponent onAuthStateChange={handleAuthStateChange} />
      {user && isLoggedIn && (
        <ChatService apiUrl={apiUrl} getToken={getToken} />
      )}
    </div>
  );
}
