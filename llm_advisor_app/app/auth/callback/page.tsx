"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/auth";

export default function AuthCallbackPage() {
  const [status, setStatus] = useState("Processing authentication...");
  const [error, setError] = useState(false);

  const router = useRouter();
  const searchParams = useSearchParams();
  const code = searchParams.get("code");
  const state = searchParams.get("state");

  const { handleGoogleCallback, isAuthenticated } = useAuth();

  // Add debug logging
  useEffect(() => {
    console.log("Auth Callback Page Loaded");
    console.log("Code:", code);
    console.log("State:", state);
  }, [code, state]);

  useEffect(() => {
    const handleCallback = async () => {
      if (!code || !state) {
        setStatus("Missing authentication parameters");
        setError(true);
        return;
      }

      // Store the code in session storage to check for double processing
      const processedCode = sessionStorage.getItem("processedOAuthCode");
      if (processedCode === code) {
        console.log("Code already processed, preventing double processing");
        setStatus("Authentication already processed");

        // Check if we're already authenticated
        if (isAuthenticated) {
          const returnUrl = localStorage.getItem("googleOAuthReturnUrl") || "/";
          router.push(returnUrl);
        } else {
          // If not authenticated, something went wrong in the first attempt
          setError(true);
          setTimeout(() => {
            router.push("/login");
          }, 2000);
        }
        return;
      }

      // Mark this code as being processed
      sessionStorage.setItem("processedOAuthCode", code);

      try {
        // Get the stored return URL or default to home
        const returnUrl = localStorage.getItem("googleOAuthReturnUrl") || "/";
        console.log("Return URL from storage:", returnUrl);
        localStorage.removeItem("googleOAuthReturnUrl"); // Clean up

        const result = await handleGoogleCallback(code, state);

        if (result.success) {
          setStatus("Authentication successful! Redirecting...");
          // Redirect to the return URL
          setTimeout(() => {
            router.push(returnUrl);
          }, 1500);
        } else {
          setStatus(`Authentication failed: ${result.message}`);
          setError(true);
          // Redirect to login after error
          setTimeout(() => {
            router.push("/login");
          }, 3000);
        }
      } catch (err) {
        console.error("Error processing authentication:", err);
        setStatus("An error occurred during authentication");
        setError(true);
        // Redirect to login after error
        setTimeout(() => {
          router.push("/login");
        }, 3000);
      }
    };

    handleCallback();
  }, [code, state, handleGoogleCallback, router]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh]">
      <div className="mb-4">
        {!error ? (
          <div className="w-16 h-16 border-t-4 border-blue-500 border-solid rounded-full animate-spin"></div>
        ) : (
          <div className="w-16 h-16 flex items-center justify-center rounded-full bg-red-100 text-red-500">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-10 w-10"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
        )}
      </div>
      <h2 className={`text-xl ${error ? "text-red-500" : "text-gray-700"}`}>
        {status}
      </h2>
      {error && (
        <p className="mt-4 text-gray-500">
          You will be redirected to the login page shortly...
        </p>
      )}
    </div>
  );
}
