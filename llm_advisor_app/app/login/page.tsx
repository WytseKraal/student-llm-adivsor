"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import AuthComponent from "@/components/auth/AuthComponent";
import { useAuth } from "@/hooks/auth";

export default function LoginPage() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  // If the user is already authenticated, redirect to home page
  useEffect(() => {
    if (isAuthenticated && !loading) {
      router.push("/");
    }
  }, [isAuthenticated, loading, router]);

  // We don't need to check for loading here since the middleware
  // and layout will handle that

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] w-full">
      <div className="w-full max-w-md">
        <h1 className="text-2xl font-bold mb-8 text-center">Welcome Back</h1>
        <AuthComponent />
      </div>
    </div>
  );
}
