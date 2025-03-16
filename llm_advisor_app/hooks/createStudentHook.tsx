export const handleCreateStudent = async (apiUrl: string,
    getToken: () => Promise<string | null>,
    studentId: string, studentName: string, studentEmail: string, birthdate: string) => {
    try {
      
      const token = await getToken();
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };
      if (token) {
        headers.Authorization = token;  // Set the Authorization header only if the token exists
      }
      const response = await fetch(`${apiUrl}/student`, {
        method: "PUT",
        headers,
        body: JSON.stringify({
          id: studentId,
          name: studentName,
          email: studentEmail,
        }),
      });
  
      const data = await response.json();
      return data.message || "Student created successfully";
    } catch (error) {
      return "Error creating student: " + (error instanceof Error ? error.message : "Unknown error");
    }
  };