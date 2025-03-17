"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/auth";
import { useRouter, useSearchParams } from "next/navigation";

export default function AuthComponent() {
  const [apiResponse, setApiResponse] = useState({
    message: "",
    isError: false,
  });
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [name, setName] = useState("");
  const [birthday, setBirthday] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [needsNewPassword, setNeedsNewPassword] = useState(false);

  const {
    signIn,
    signUp,
    completeNewPasswordChallenge,
    initiateGoogleSignIn,
    handleGoogleCallback,
  } = useAuth();

  const router = useRouter();
  const searchParams = useSearchParams();
  const returnUrl = searchParams.get("returnUrl") || "/";
  const code = searchParams.get("code");
  const state = searchParams.get("state");

  // Handle Google OAuth callback
  useEffect(() => {
    const handleCallback = async () => {
      if (code && state) {
        setLoading(true);
        setApiResponse({
          message: "Processing Google sign-in...",
          isError: false,
        });

        try {
          const result = await handleGoogleCallback(code, state);
          if (result.success) {
            setApiResponse({
              message: "Successfully signed in with Google!",
              isError: false,
            });

            // Redirect to the returnUrl or dashboard
            setTimeout(() => {
              router.push(returnUrl);
            }, 1000);
          } else {
            setApiResponse({ message: result.message, isError: true });
          }
        } catch (error) {
          console.error("Google sign-in error:", error);
          if (error instanceof Error) {
            setApiResponse({ message: error.message, isError: true });
          } else {
            setApiResponse({
              message: "An unknown error occurred",
              isError: true,
            });
          }
        } finally {
          setLoading(false);
        }
      }
    };

    handleCallback();
  }, [code, state, handleGoogleCallback, router, returnUrl]);

  const handleSignIn = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    setLoading(true);
    setApiResponse({ message: "", isError: false });

    try {
      const result = await signIn(email, password);
      console.log(result);
      if (!result.success) {
        if (result.requiresNewPassword) {
          setNeedsNewPassword(true);
        } else {
          setApiResponse({ message: result.message, isError: true });
        }
      } else {
        setApiResponse({ message: "Successfully signed in!", isError: false });

        // Redirect to the returnUrl or dashboard
        setTimeout(() => {
          router.push(returnUrl);
        }, 1000);
      }
    } catch (error) {
      console.error("Sign in error:", error);
      if (error instanceof Error) {
        setApiResponse({ message: error.message, isError: true });
      } else {
        setApiResponse({ message: "An unknown error occurred", isError: true });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = () => {
    setLoading(true);
    setApiResponse({ message: "Redirecting to Google...", isError: false });
    initiateGoogleSignIn(returnUrl);
  };

  const handleSignUp = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    setLoading(true);
    setApiResponse({ message: "", isError: false });

    try {
      await signUp(email, password, name, birthday);

      setApiResponse({
        message: "Registration successful!",
        isError: false,
      });

      // Switch to login form after successful registration
      setTimeout(() => {
        setIsRegistering(false);
      }, 3000);
    } catch (error) {
      console.error("Registration error:", error);
      if (error instanceof Error) {
        setApiResponse({ message: error.message, isError: true });
      } else {
        setApiResponse({
          message: "An unknown error occurred during registration",
          isError: true,
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNewPassword = async (e: { preventDefault: () => void }) => {
    e.preventDefault();
    setLoading(true);
    setApiResponse({ message: "", isError: false });

    try {
      await completeNewPasswordChallenge(newPassword, name);

      setApiResponse({
        message: "Successfully set new password! Redirecting...",
        isError: false,
      });

      // Redirect to the returnUrl or dashboard
      setTimeout(() => {
        router.push(returnUrl);
      }, 1000);
    } catch (error) {
      console.error("New password error:", error);
      if (error instanceof Error) {
        setApiResponse({ message: error.message, isError: true });
      } else {
        setApiResponse({ message: "An unknown error occurred", isError: true });
      }
    } finally {
      setLoading(false);
    }
  };

  const toggleRegistration = () => {
    setIsRegistering(!isRegistering);
    setApiResponse({ message: "", isError: false });
  };

  if (needsNewPassword) {
    return (
      <div className="flex flex-col items-center w-full max-w-md">
        <form
          onSubmit={handleNewPassword}
          className="flex flex-col gap-4 w-full p-6 bg-white rounded-lg shadow-md"
        >
          <h2 className="text-xl font-bold text-center">Set New Password</h2>

          <div className="space-y-1">
            <Input
              type="password"
              placeholder="New Password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1">
            <Input
              type="text"
              placeholder="Your Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Processing..." : "Set New Password"}
          </Button>
        </form>

        {apiResponse.message && (
          <p
            className={`mt-4 text-center ${
              apiResponse.isError ? "text-red-500" : "text-green-500"
            }`}
          >
            {apiResponse.message}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center w-full max-w-md">
      {isRegistering ? (
        <form
          onSubmit={handleSignUp}
          className="flex flex-col gap-4 w-full p-6 bg-white rounded-lg shadow-md"
        >
          <h2 className="text-xl font-bold text-center">
            Register for an Account
          </h2>

          <div className="space-y-1">
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1">
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1">
            <Input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="flex flex-col space-y-1">
            <label htmlFor="birthday" className="text-sm text-gray-500">
              Birthday
            </label>
            <Input
              id="birthday"
              type="date"
              value={birthday}
              onChange={(e) => setBirthday(e.target.value)}
              required
            />
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Registering..." : "Register"}
          </Button>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or</span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={handleGoogleSignIn}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2"
          >
            <svg
              viewBox="0 0 24 24"
              width="24"
              height="24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <g transform="matrix(1, 0, 0, 1, 0, 0)">
                <path
                  d="M21.35,11.1H12.18V13.83H18.69C18.36,17.64 15.19,19.27 12.19,19.27C8.36,19.27 5,16.25 5,12C5,7.9 8.2,4.73 12.2,4.73C15.29,4.73 17.1,6.7 17.1,6.7L19,4.72C19,4.72 16.56,2 12.1,2C6.42,2 2.03,6.8 2.03,12C2.03,17.05 6.16,22 12.25,22C17.6,22 21.5,18.33 21.5,12.91C21.5,11.76 21.35,11.1 21.35,11.1Z"
                  fill="#4285F4"
                ></path>
              </g>
            </svg>
            Register with Google
          </Button>

          <p className="text-center text-sm">
            Already have an account?{" "}
            <button
              type="button"
              className="text-blue-500 hover:underline"
              onClick={toggleRegistration}
            >
              Sign in
            </button>
          </p>
        </form>
      ) : (
        <form
          onSubmit={handleSignIn}
          className="flex flex-col gap-4 w-full p-6 bg-white rounded-lg shadow-md"
        >
          <h2 className="text-xl font-bold text-center">Sign In</h2>

          <div className="space-y-1">
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1">
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <Button type="submit" disabled={loading} className="w-full">
            {loading ? "Signing in..." : "Sign In"}
          </Button>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or</span>
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            onClick={handleGoogleSignIn}
            disabled={loading}
            className="w-full flex items-center justify-center gap-2"
          >
            <svg
              viewBox="0 0 24 24"
              width="24"
              height="24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <g transform="matrix(1, 0, 0, 1, 0, 0)">
                <path
                  d="M21.35,11.1H12.18V13.83H18.69C18.36,17.64 15.19,19.27 12.19,19.27C8.36,19.27 5,16.25 5,12C5,7.9 8.2,4.73 12.2,4.73C15.29,4.73 17.1,6.7 17.1,6.7L19,4.72C19,4.72 16.56,2 12.1,2C6.42,2 2.03,6.8 2.03,12C2.03,17.05 6.16,22 12.25,22C17.6,22 21.5,18.33 21.5,12.91C21.5,11.76 21.35,11.1 21.35,11.1Z"
                  fill="#4285F4"
                ></path>
              </g>
            </svg>
            Sign in with Google
          </Button>

          <p className="text-center text-sm">
            No account?{" "}
            <button
              type="button"
              className="text-blue-500 hover:underline"
              onClick={toggleRegistration}
            >
              Register
            </button>
          </p>
        </form>
      )}

      {apiResponse.message && (
        <p
          className={`mt-4 text-center ${
            apiResponse.isError ? "text-red-500" : "text-green-500"
          }`}
        >
          {apiResponse.message}
        </p>
      )}
    </div>
  );
}
