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
  const [birthday, setBirthday] = useState("");
  const [loading, setLoading] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);

  const {
    user,
    signIn,
    signUp,
    completeNewPasswordChallenge,
    challengeUser,
    verifyStudentExists,
    signOut,
  } = useAuth();

  useEffect(() => {
    if (user) {
      checkUserIsStudent();
    }
  }, [user]);

  const checkUserIsStudent = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const isStudent = await verifyStudentExists();

      if (isStudent) {
        onAuthStateChange(true);
      } else {
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
      const result = await signIn(email, password);

      if (
        "challengeName" in result &&
        result.challengeName === "NEW_PASSWORD_REQUIRED"
      ) {
        setApiResponse("Please set a new password");
        setLoading(false);
        return;
      }

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

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setApiResponse("");

    try {
      await signUp(email, password, name, birthday);

      setApiResponse(
        "Registration successful! Please check your email for verification and then sign in."
      );

      setIsRegistering(false);
    } catch (error) {
      console.error("Registration error:", error);
      if (error instanceof Error) {
        setApiResponse(error.message);
      } else {
        setApiResponse("An unknown error occurred during registration");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleNewPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setApiResponse("");

    try {
      await completeNewPasswordChallenge(newPassword, name);

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

  const toggleRegistration = () => {
    setIsRegistering(!isRegistering);
    setApiResponse("");
  };

  if (!user && !challengeUser) {
    return (
      <div className="flex flex-col items-center w-full max-w-md">
        {isRegistering ? (
          <form onSubmit={handleSignUp} className="flex flex-col gap-4 w-full">
            <h2 className="text-xl font-bold text-center">
              Register for an Account
            </h2>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Input
              type="text"
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <div className="flex flex-col">
              <label htmlFor="birthday" className="text-sm mb-1">
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
            <Button type="submit" disabled={loading}>
              {loading ? "Registering..." : "Register"}
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
          <form onSubmit={handleSignIn} className="flex flex-col gap-4 w-full">
            <h2 className="text-xl font-bold text-center">Sign In</h2>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <Button type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </Button>
            <p className="text-center text-sm">
              Don't have an account?{" "}
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
        {apiResponse && (
          <p
            className={`mt-4 ${
              apiResponse.includes("failed") || apiResponse.includes("error")
                ? "text-red-500"
                : apiResponse.includes("successful")
                ? "text-green-500"
                : ""
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
