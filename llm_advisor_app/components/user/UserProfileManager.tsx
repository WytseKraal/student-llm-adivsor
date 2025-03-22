//#############################################
// File: UserProfileManager.tsx
// Components for viewing profile and changing email/preferred name
//#############################################
"use client";

import { useState, useEffect } from "react";
import { useUserData } from "@/hooks/userDataHook";
import { useStudentData } from "@/hooks/studentDataHook";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2, Pencil, Check, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface UserProfileProps {
  apiUrl: string;
  getToken: () => Promise<string | null>;
}

export default function UserProfile({ apiUrl, getToken }: UserProfileProps) {
  const { sub, isLoading, error } = useUserData();
  const [isLoadingStudent, setIsLoadingStudent] = useState<boolean>(false);
  const [studentPreferredName, setStudentPreferredName] = useState<string>("");
  const [studentEmail, setStudentEmail] = useState<string>("");
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [responseMessage, setResponseMessage] = useState<string>("");

  const { studentData } = useStudentData(sub, apiUrl, getToken, setIsLoadingStudent);

  useEffect(() => {
    if (studentData) {
      setStudentPreferredName(studentData.preferredName || "");
      setStudentEmail(studentData.email || "");
    }
  }, [studentData]);

  const handleUpdateStudent = async () => {
    if (!studentData) return;

    setIsSaving(true);
    try {
      const token = await getToken();
      const headers: HeadersInit = {
        "Content-Type": "application/json",
        ...(token ? { Authorization: token } : {}),
      };

      const response = await fetch(`${apiUrl}/student`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({ id: sub, preferredName: studentPreferredName, email: studentEmail }),
      });

      if (!response.ok) throw new Error("Failed to update student");

      studentData.preferredName  = studentPreferredName;
      studentData.email = studentEmail;
      setResponseMessage("Student updated successfully!");
      setIsEditing(false);
    } catch (error) {
      console.error("Error updating student:", error);
      setResponseMessage("Error updating student.");
    } finally {
      setIsSaving(false);
    }
  };

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
          <div className="text-red-500 flex justify-center">Error loading user data</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full shadow-lg">
      <CardHeader className="border-b flex justify-between items-center">
        <CardTitle className="text-lg">Student Profile</CardTitle>
        {!isEditing ? (
          <Button variant="ghost" size="icon" onClick={() => setIsEditing(true)}>
            <Pencil className="h-4 w-4" />
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button variant="ghost" size="icon" onClick={handleUpdateStudent} disabled={isSaving}>
              {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Check className="h-4 w-4 text-green-500" />}
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setIsEditing(false)} disabled={isSaving}>
              <X className="h-4 w-4 text-red-500" />
            </Button>
          </div>
        )}
      </CardHeader>
      <CardContent className="pt-6">
        <div className="flex items-start gap-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${studentPreferredName || studentData?.name}`} />
            <AvatarFallback className="bg-primary text-primary-foreground text-lg">
              {studentPreferredName?.charAt(0) || studentData?.name?.charAt(0) || "S"}
            </AvatarFallback>
          </Avatar>

          <div className="space-y-3 w-full">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Name</p>
              <p className="font-medium">{studentData?.name || "Not provided"}</p>
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Preferred Name</p>
              {isEditing ? (
                <Input value={studentPreferredName} onChange={(e) => setStudentPreferredName(e.target.value)} />
              ) : (
                <p className="font-medium">{studentData?.preferredName || "Not provided"}</p>
              )}
            </div>

            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Email</p>
              {isEditing ? (
                <Input value={studentEmail} onChange={(e) => setStudentEmail(e.target.value)} />
              ) : (
                <p className="font-medium">{studentData?.email || "Not provided"}</p>
              )}
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

        {responseMessage && <p className="mt-2 text-sm text-green-600">{responseMessage}</p>}
      </CardContent>
    </Card>
  );
}
