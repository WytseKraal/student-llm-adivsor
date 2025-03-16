"use client";
import { useEffect } from "react";
import { useAuth } from "@/hooks/auth";
import { env } from "@/environment";
import ChatService from "@/components/user/ChatService";
import { useRouter } from "next/navigation";

export default function ChatPage() {
  const { isAuthenticated, loading, getToken } = useAuth();
  const router = useRouter();
  const apiUrl = env.apiUrl;

  // If not authenticated, redirect to login page with return URL
  useEffect(() => {
    if (!isAuthenticated && !loading) {
      router.push("/login?returnUrl=/chat");
    }
  }, [isAuthenticated, loading, router]);

  return (
    <div className="flex flex-col items-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      {isAuthenticated ? (
        <ChatService apiUrl={apiUrl} getToken={getToken} />
      ) : (
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">Loading chat service...</p>
        </div>
      )}
    </div>
  );
}
