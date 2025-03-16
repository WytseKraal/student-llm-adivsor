"use client";
import { useEffect } from "react";
import { useAuth } from "@/hooks/auth";
import { env } from "@/environment";
import AuthComponent from "@/components/auth/AuthComponent";

export default function ProfilePage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  // If not authenticated, redirect to login page with return URL
  useEffect(() => {
    if (!isAuthenticated && !loading) {
      router.push("/login?returnUrl=/profile");
    }
  }, [isAuthenticated, loading, router]);

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      {isAuthenticated ? (
        <div className="w-full max-w-3xl">
          <h1 className="text-2xl font-bold mb-8">Your Profile</h1>
          <UserProfile />
        </div>
      ) : (
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading profile...</p>
        </div>
      )}
    </div>
  );
}
