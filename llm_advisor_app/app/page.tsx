"use client";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useAuth } from "@/hooks/auth";
import { Input } from "@/components/ui/input";

export default function Home() {
  const [apiResponse, setApiResponse] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [name, setName] = useState("");
  const [showText, setShowText] = useState(false);
  const {
    user,
    signIn,
    signOut,
    getToken,
    completeNewPasswordChallenge,
    challengeUser,
  } = useAuth();

  // const apiUrl = "https://26jbdrdk5g.execute-api.eu-north-1.amazonaws.com/Prod";

  const apiUrl = "http://127.0.0.1:3001";

  async function callProtectedApi() {
    try {
      const token = await getToken();
      const res = await fetch(`${apiUrl}/hello`, {
        headers: {
          Authorization: token,
        },
      });
      const data = await res.json();
      console.log("API Response:", data);
      setApiResponse(data.message);
    } catch (error) {
      console.error("Error:", error);
      setApiResponse("An error occurred");
    }
  }

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
    } catch (error) {
      console.error("New password error:", error);
      if (error instanceof Error) {
        setApiResponse(error.message);
      } else {
        setApiResponse("An unknown error occurred");
      }
    }
  };

  const handleToggleText = () => {
    setShowText(!showText);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <h1 className="text-2xl font-bold mb-8">Protected API Test</h1>

      {!user && !challengeUser ? (
        <form
          onSubmit={handleSignIn}
          className="flex flex-col gap-4 w-full max-w-md"
        >
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
      ) : challengeUser ? (
        <form
          onSubmit={handleNewPassword}
          className="flex flex-col gap-4 w-full max-w-md"
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
      ) : (
        <div className="flex flex-col gap-4 items-center">
          <p>Welcome, {user?.getUsername()}!</p>
          <Button onClick={callProtectedApi}>Call Protected API</Button>
          <Button variant="outline" onClick={signOut}>
            Sign Out
          </Button>
        </div>
      )}

      {apiResponse && <p className="mt-4">Response: {apiResponse}</p>}

      <Button onClick={handleToggleText} className="mt-4">
        Toggle Text
      </Button>
      {showText && <p className="mt-4">This is the toggled text!</p>}
    </div>
  );
}
