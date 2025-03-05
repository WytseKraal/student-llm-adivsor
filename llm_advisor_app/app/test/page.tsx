"use client";
import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/auth";
import { env } from "@/environment";
import AuthComponent from "@/components/auth/AuthComponent";
import ApiService from "@/components/testing/ApiTest";
import UserProfile from "@/components/user/UserProfile";
import StudentManager from "@/components/database_interaction";

export default function Test() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const { user, getToken } = useAuth();
  const apiUrl = env.apiUrl;

  useEffect(() => {
    if (user) {
      setIsLoggedIn(true);
    }
  }, [user]);

  const handleAuthStateChange = (loggedIn: boolean) => {
    setIsLoggedIn(loggedIn);
  };

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <AuthComponent onAuthStateChange={handleAuthStateChange} />

      {user && isLoggedIn && (
        <div className="flex flex-col gap-8 items-center w-full max-w-md mt-8">
          <UserProfile />
          <ApiService getToken={getToken} />
          <StudentManager apiUrl={apiUrl} getToken={getToken} />
        </div>
      )}
    </div>
  );
}
