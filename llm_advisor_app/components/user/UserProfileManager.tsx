"use client";

import {useState} from "react";
import { useUserData } from "@/hooks/userDataHook";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2 } from "lucide-react";
import { useStudentData } from "@/hooks/studentDataHook";

interface UserProfileProps {
  apiUrl: string;
  getToken: () => Promise<string | null>;
}

export default function UserProfile({ apiUrl, getToken }: UserProfileProps) {
  const { sub, isLoading, error } = useUserData();
  const [isLoadingStudent, setIsLoadingStudent] = useState<boolean>(false);
  const { studentData } = useStudentData(sub,
    apiUrl,
    getToken,
    setIsLoadingStudent
  );

  if (isLoading || isLoadingStudent) {
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

  /*/ Get user initials for avatar fallback
  const getInitials = () => {
    if (!userName) return "U";
    return userName
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .substring(0, 2);
  };*/

  return (
    <Card className="w-full shadow-lg">
    <CardHeader className="border-b">
      <CardTitle className="text-lg">Student Profile</CardTitle>
    </CardHeader>
    <CardContent className="pt-6">
      <div className="flex items-start gap-4">
        <Avatar className="h-16 w-16">
          <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${studentData?.preferredName || studentData?.name}`} />
          <AvatarFallback className="bg-primary text-primary-foreground text-lg">
            {studentData?.preferredName?.charAt(0) || studentData?.name?.charAt(0) || "S"}
          </AvatarFallback>
        </Avatar>

        <div className="space-y-3">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Name</p>
            <p className="font-medium">{studentData?.name || "Not provided"}</p>
          </div>

          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Preferred Name</p>
            <p className="font-medium">{studentData?.preferredName || "Not provided"}</p>
          </div>

          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Email</p>
            <p className="font-medium">{studentData?.email || "Not provided"}</p>
          </div>

          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Program</p>
            <p className="font-medium">{studentData?.program || "Not provided"}</p>
          </div>

          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Year</p>
            <p className="font-medium">{studentData?.year || "Not provided"}</p>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>
  );
}
