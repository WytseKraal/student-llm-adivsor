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
  const { user, signIn, completeNewPasswordChallenge, challengeUser } =
    useAuth();

  useEffect(() => {
    if (user) {
      onAuthStateChange(true);
    }
  }, [user, onAuthStateChange]);

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await signIn(email, password);
      if (
        "challengeName" in result &&
        result.challengeName === "NEW_PASSWORD_REQUIRED"
      ) {
        setApiResponse("Please set a new password");
      } else {
        setApiResponse("Successfully signed in!");
        onAuthStateChange(true);
      }
    } catch (error) {
      console.error("Sign in error:", error);
      if (error instanceof Error) {
        setApiResponse(error.message);
      } else {
        setApiResponse("An unknown error occurred");
      }
    }
  };

  const handleNewPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await completeNewPasswordChallenge(newPassword, name);
      setApiResponse("Successfully set new password!");
      setNewPassword("");
      onAuthStateChange(true);
    } catch (error) {
      console.error("New password error:", error);
      if (error instanceof Error) {
        setApiResponse(error.message);
      } else {
        setApiResponse("An unknown error occurred");
      }
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
          <Button type="submit">Sign In</Button>
        </form>
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
          <Button type="submit">Set New Password</Button>
        </form>
        {apiResponse && <p className="mt-4">Response: {apiResponse}</p>}
      </div>
    );
  }

  // When logged in, just display any response message or nothing
  return apiResponse ? <p className="mt-4">Response: {apiResponse}</p> : null;
}
