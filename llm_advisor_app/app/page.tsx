"use client";
import { useEffect } from "react";
import { useAuth } from "@/hooks/auth";
import { useRouter } from "next/navigation";
import FancyTitle from "@/components/styling/FancyTitle";

export default function Home() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated && !loading) {
      router.push("/login");
    }
  }, [isAuthenticated, loading, router]);

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      {isAuthenticated && (
        <>
          <FancyTitle />
          <div className="mt-10 max-w-3xl text-center">
            <h2 className="text-2xl font-semibold mb-4">
              Welcome to your dashboard
            </h2>
            <p className="text-gray-600">
              You are now logged in. This is your protected homepage.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
