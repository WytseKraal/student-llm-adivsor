"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function Home() {
  const [apiResponse, setApiResponse] = useState("");

  const apiUrl = "http://127.0.0.1:3001";
  const apiKey = "RATE_LMITER";

  async function callLocalApi() {
    try {
      const res = await fetch(`${apiUrl}/hello`, {
        headers: {
          "x-api-key": apiKey,
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

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <h1>Call Local API from Next.js</h1>
      <Button onClick={callLocalApi}>Call /hello</Button>
      <p>Response: {apiResponse}</p>
    </div>
  );
}
