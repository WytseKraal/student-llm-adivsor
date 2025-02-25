"use client";
import { useUserData } from "@/hooks/userDataHook";

export default function UserProfile() {
  const { userName, userEmail, sub, isLoading, error } = useUserData();

  if (isLoading) {
    return <p>Loading user data...</p>;
  }

  if (error) {
    return <p>Error loading user data</p>;
  }

  return (
    <div className="flex flex-col gap-2 w-full">
      <p>Name: {userName}</p>
      <p>Email: {userEmail}</p>
      <p>Sub: {sub}</p>
    </div>
  );
}
