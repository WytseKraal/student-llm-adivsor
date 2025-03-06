"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/auth";

interface AuthComponentProps {
  onAuthStateChange: (isLoggedIn: boolean) => void;
}

export default function AuthComponent({
  onAuthStateChange,
}: AuthComponentProps) {
  const [apiResponse, setApiResponse] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  const {
    user,
    signIn,
    completeNewPasswordChallenge,
    challengeUser,
    verifyStudentExists,
    signOut,
  } = useAuth();

  useEffect(() => {
    // Check if user exists and then verify if they're in the student database
    if (user) {
      checkUserIsStudent();
    }
  }, [user]);

  const checkUserIsStudent = async () => {
    if (!user) return;

    setLoading(true);
    try {
      // Verify that the user's sub exists in the student database
      const isStudent = await verifyStudentExists();

      if (isStudent) {
        // User is a valid student, allow access
        onAuthStateChange(true);
      } else {
        // User is not in student database, sign them out
        setApiResponse(
          "Login failed: Your account is not registered as a student"
        );
        signOut();
      }
    } catch (error) {
      console.error("Error verifying student status:", error);
      setApiResponse("Error verifying student status. Please try again.");
      signOut();
    } finally {
      setLoading(false);
    }
  };

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setApiResponse("");

    try {
      // Attempt to sign in with Cognito
      const result = await signIn(email, password);

      // If new password is required, we'll handle that in the next step
      if (
        "challengeName" in result &&
        result.challengeName === "NEW_PASSWORD_REQUIRED"
      ) {
        setApiResponse("Please set a new password");
        setLoading(false);
        return;
      }

      // The student verification happens in the useEffect when user changes
      setApiResponse("Successfully signed in! Verifying student status...");
    } catch (error) {
      console.error("Sign in error:", error);
      if (error instanceof Error) {
        setApiResponse(error.message);
      } else {
        setApiResponse("An unknown error occurred");
      }
      setLoading(false);
    }
  };

  const handleNewPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setApiResponse("");

    try {
      // Complete the new password challenge
      await completeNewPasswordChallenge(newPassword, name);

      // The student verification happens in the useEffect when user changes
      setApiResponse(
        "Successfully set new password! Verifying student status..."
      );
      setNewPassword("");
    } catch (error) {
      console.error("New password error:", error);
      if (error instanceof Error) {
        setApiResponse(error.message);
      } else {
        setApiResponse("An unknown error occurred");
      }
      setLoading(false);
    }
  };

  if (!user && !challengeUser) {
    return (
      <div className="flex flex-col items-center w-full max-w-md">
        <form onSubmit={handleSignIn} className="flex flex-col gap-4 w-full">
          <Input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign In"}
          </Button>
        </form>
        {apiResponse && (
          <p
            className={`mt-4 ${
              apiResponse.includes("failed") ? "text-red-500" : ""
            }`}
          >
            {apiResponse}
          </p>
        )}
      </div>
    );
  }

  if (challengeUser) {
    return (
      <div className="flex flex-col items-center w-full max-w-md">
        <form
          onSubmit={handleNewPassword}
          className="flex flex-col gap-4 w-full"
        >
          <Input
            type="password"
            placeholder="New Password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <Input
            type="text"
            placeholder="Your Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Button type="submit" disabled={loading}>
            {loading ? "Processing..." : "Set New Password"}
          </Button>
        </form>
        {apiResponse && (
          <p
            className={`mt-4 ${
              apiResponse.includes("failed") ? "text-red-500" : ""
            }`}
          >
            {apiResponse}
          </p>
        )}
      </div>
    );
  }

  // When logged in, show loading or success message
  return (
    <div className="flex justify-center items-center">
      {loading ? (
        <p>Verifying student status...</p>
      ) : (
        apiResponse && <p className="mt-4">{apiResponse}</p>
      )}
    </div>
  );
}
