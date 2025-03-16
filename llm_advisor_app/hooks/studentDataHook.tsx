import { useState, useEffect } from "react";

interface StudentData {
  id: string;
  name: string;
  email: string;
  preferredName: string;
  program: string;
  year: string;
}

export const useStudentData = (
  searchId: string,
  apiUrl: string,
  getToken: () => Promise<string | null>,
  setIsLoadingStudent: (bool: boolean) => void
) => {
  const [studentData, setStudentData] = useState<StudentData | null>(null);
  const [responseMessage, setResponseMessage] = useState<string>("");
  
 
  useEffect(() => {
    if (searchId === "") return;
  // Handle getting student data
  const handleGetStudent = async () => {
 
    setIsLoadingStudent(true);
    try {
      const token = await getToken();
       // Only set Authorization header if token is not null
    const headers: HeadersInit = {
        "Content-Type": "application/json",
      };
  
      if (token) {
        headers.Authorization = token;  // Set the Authorization header only if the token exists
      }
  
      const response = await fetch(`${apiUrl}/student?id=${searchId}`, { headers });
      const data = await response.json();
      if (response.ok) {
        const formattedData: StudentData = {
          id: data.STUDENT_ID,
          name: `${data.FIRST_NAME} ${data.LAST_NAME}`, // Combine first and last name
          email: data.EMAIL,
          preferredName: data.PREFERRED_NAME,
          program: data.PROGRAM,
          year: data.YEAR,
        };
        console.log(formattedData);
        setStudentData(formattedData);
        setResponseMessage("Student found!");
      } else {
        setResponseMessage(data.error || "Error retrieving student");
        setStudentData(null);
      }
    } catch (error) {
      setResponseMessage(
        "Error retrieving student: " + (error instanceof Error ? error.message : "Unknown error")
      );
      setStudentData(null);
    } finally {
      setIsLoadingStudent(false);
    }
  };
  
  handleGetStudent();
}, [searchId, apiUrl, getToken]);
  return {
    studentData,
    responseMessage,
  };
};