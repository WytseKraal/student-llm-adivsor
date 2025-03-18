"use client";

import { useState } from "react";
import { useUserData } from "@/hooks/userDataHook";
import { useStudentData } from "@/hooks/studentDataHook";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Loader2 } from "lucide-react";

interface UserProfileProps {
  apiUrl: string;
  getToken: () => Promise<string | null>;
}

export default function UserProfile({ apiUrl, getToken }: UserProfileProps) {
  const { sub, isLoading, error } = useUserData();
  const [isLoadingStudent, setIsLoadingStudent] = useState<boolean>(false);
  const { studentData } = useStudentData(sub, apiUrl, getToken, setIsLoadingStudent);

  // State for updating student details
  const [studentPreferredName, setStudentPreferredName] = useState<string>(studentData?.preferredName || "");
  const [studentEmail, setStudentEmail] = useState<string>(studentData?.email || "");
  const [responseMessage, setResponseMessage] = useState<string>("");

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

  // Handle student update
  const handleUpdateStudent = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const token = await getToken();

      if(studentEmail == "") {
        setResponseMessage("Email was not provided.");
        return;
      }

      const response = await fetch(`${apiUrl}/student`, {
        method: "PATCH",
        headers: {
          Authorization: token || "",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id: sub,
          preferredName: studentPreferredName,
          email: studentEmail,
        }),
      });

      if (response.ok) {
        setResponseMessage("Student updated successfully!");
      } else {
        setResponseMessage("Failed to update student.");
      }
    } catch (error) {
      setResponseMessage("Error updating student.");
    }
  };

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

        {/* Update Student Form */}
        <div className="mt-6 border-t pt-6">
          <h3 className="text-lg font-semibold">Update Student Information</h3>
          <form onSubmit={handleUpdateStudent} className="flex flex-col gap-2 mt-4">
            <label className="flex flex-col">
              <span className="text-sm text-muted-foreground">Preferred Name</span>
              <input
                type="text"
                value={studentPreferredName}
                onChange={(e) => setStudentPreferredName(e.target.value)}
                className="border p-2 rounded"
              />
            </label>
            <label className="flex flex-col">
              <span className="text-sm text-muted-foreground">Email</span>
              <input
                type="email"
                value={studentEmail}
                onChange={(e) => setStudentEmail(e.target.value)}
                className="border p-2 rounded"
              />
            </label>
            <button type="submit" className="bg-blue-500 text-white p-2 rounded">
              Update Student
            </button>
          </form>
          {responseMessage && <p className="mt-2 text-sm text-green-600">{responseMessage}</p>}
        </div>
      </CardContent>
    </Card>
  );
}