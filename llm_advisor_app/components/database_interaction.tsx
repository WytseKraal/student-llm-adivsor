import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface StudentData {
  id: string;
  name: string;
  email: string;
}

interface StudentManagerProps {
  apiUrl: string;
  getToken: () => Promise<string>;
}

const StudentManager: React.FC<StudentManagerProps> = ({
  apiUrl,
  getToken,
}) => {
  const [studentId, setStudentId] = useState<string>("");
  const [studentName, setStudentName] = useState<string>("");
  const [studentEmail, setStudentEmail] = useState<string>("");
  const [searchId, setSearchId] = useState<string>("");
  const [responseMessage, setResponseMessage] = useState<string>("");
  const [studentData, setStudentData] = useState<StudentData | null>(null);

  const handleCreateStudent = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const token = await getToken();
      const response = await fetch(`${apiUrl}/student`, {
        method: "PUT",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id: studentId,
          name: studentName,
          email: studentEmail,
        }),
      });

      const data = await response.json();
      setResponseMessage(data.message || "Student created successfully");

      // Clear form
      setStudentId("");
      setStudentName("");
      setStudentEmail("");
    } catch (error) {
      setResponseMessage(
        "Error creating student: " +
          (error instanceof Error ? error.message : "Unknown error")
      );
    }
  };

  const handleGetStudent = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const token = await getToken();
      const response = await fetch(`${apiUrl}/student?id=${searchId}`, {
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();
      if (response.ok) {
        setStudentData(data as StudentData);
        setResponseMessage("Student found!");
      } else {
        setResponseMessage(data.error || "Error retrieving student");
        setStudentData(null);
      }
    } catch (error) {
      setResponseMessage(
        "Error retrieving student: " +
          (error instanceof Error ? error.message : "Unknown error")
      );
      setStudentData(null);
    }
  };

  return (
    <div className="flex flex-col gap-8 w-full max-w-2xl">
      <Card>
        <CardHeader>
          <CardTitle>Create/Update Student</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreateStudent} className="flex flex-col gap-4">
            <Input
              placeholder="Student ID"
              value={studentId}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setStudentId(e.target.value)
              }
            />
            <Input
              placeholder="Name"
              value={studentName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setStudentName(e.target.value)
              }
            />
            <Input
              placeholder="Email"
              type="email"
              value={studentEmail}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setStudentEmail(e.target.value)
              }
            />
            <Button type="submit">Save Student</Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Retrieve Student</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleGetStudent} className="flex flex-col gap-4">
            <Input
              placeholder="Student ID"
              value={searchId}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setSearchId(e.target.value)
              }
            />
            <Button type="submit">Search</Button>
          </form>

          {studentData && (
            <div className="mt-4 p-4 bg-gray-100 rounded-lg">
              <h3 className="font-semibold mb-2">Student Information:</h3>
              <p>ID: {studentData.id}</p>
              <p>Name: {studentData.name}</p>
              <p>Email: {studentData.email}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {responseMessage && <p className="text-center mt-4">{responseMessage}</p>}
    </div>
  );
};

export default StudentManager;
