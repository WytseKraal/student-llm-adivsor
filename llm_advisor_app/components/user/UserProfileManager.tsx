"use client";

import { useUserData } from "@/hooks/userDataHook";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2 } from "lucide-react";

export default function UserProfile() {
  const { userName, userEmail, sub, isLoading, error } = useUserData();

  if (isLoading) {
    return (
      <Card className="w-full shadow-lg">
        <CardHeader className="border-b">
          <CardTitle className="text-lg">User Profile</CardTitle>
        </CardHeader>
        <CardContent className="pt-6 pb-6 flex justify-center items-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full shadow-lg">
        <CardHeader className="border-b">
          <CardTitle className="text-lg">User Profile</CardTitle>
        </CardHeader>
        <CardContent className="pt-6 pb-6">
          <div className="text-red-500 flex justify-center">
            Error loading user data
          </div>
        </CardContent>
      </Card>
    );
  }

  // Get user initials for avatar fallback
  const getInitials = () => {
    if (!userName) return "U";
    return userName
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .substring(0, 2);
  };

  return (
    <Card className="w-full shadow-lg">
      <CardHeader className="border-b">
        <CardTitle className="text-lg">User Profile</CardTitle>
      </CardHeader>
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <Avatar className="h-16 w-16">
            <AvatarImage
              src={`https://api.dicebear.com/7.x/initials/svg?seed=${getInitials()}`}
            />
            <AvatarFallback className="bg-primary text-primary-foreground text-lg">
              {getInitials()}
            </AvatarFallback>
          </Avatar>

          <div className="space-y-3">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Name</p>
              <p className="font-medium">{userName || "Not provided"}</p>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Email</p>
              <p className="font-medium">{userEmail || "Not provided"}</p>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">User ID</p>
              <p className="font-medium text-sm">{sub || "Not provided"}</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
