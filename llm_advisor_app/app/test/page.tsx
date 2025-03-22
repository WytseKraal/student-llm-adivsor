//#############################################
// File: page.tsx
// UI for test page
//#############################################
"use client";
import { useEffect } from "react";
import { useAuth } from "@/hooks/auth";
import { env } from "@/environment";
import { useRouter } from "next/navigation";
import ApiService from "@/components/testing/ApiTest";
import UserProfile from "@/components/user/UserProfile";
import StudentManager from "@/components/database_interaction";

export default function TestPage() {
  const { isAuthenticated, loading, getToken } = useAuth();
  const router = useRouter();
  const apiUrl = env.apiUrl;

  // If not authenticated, redirect to login page with return URL
  useEffect(() => {
    if (!isAuthenticated && !loading) {
      router.push("/login?returnUrl=/test");
    }
  }, [isAuthenticated, loading, router]);

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      {isAuthenticated ? (
        <div className="w-full max-w-4xl">
          <h1 className="text-2xl font-bold mb-8 text-center">Test Page</h1>

          <div className="flex flex-col gap-8 items-center w-full mt-8">
            <UserProfile />
            <ApiService getToken={getToken} />
            <StudentManager apiUrl={apiUrl} getToken={getToken} />
          </div>
        </div>
      ) : (
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading test components...</p>
        </div>
      )}
    </div>
  );
}
