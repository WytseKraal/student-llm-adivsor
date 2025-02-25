"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { env } from "@/environment";

interface ApiServiceProps {
  getToken: () => Promise<string>;
}

export default function ApiService({ getToken }: ApiServiceProps) {
  const [apiResponse, setApiResponse] = useState("");
  const apiUrl = env.apiUrl;

  async function callHelloApi() {
    try {
      const token = await getToken();
      const res = await fetch(`${apiUrl}/hello`, {
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
      });
      const data = await res.json();
      console.log("Hello API Response:", data);
      setApiResponse(`Hello: ${data.message}`);
    } catch (error) {
      console.error("Error calling /hello endpoint:", error);
      setApiResponse("An error occurred calling /hello endpoint");
    }
  }

  async function callByeApi() {
    try {
      const token = await getToken();
      const res = await fetch(`${apiUrl}/goodbye/bye`, {
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
      });
      const data = await res.json();
      console.log("Goodbye Bye API Response:", data);
      setApiResponse(`Goodbye Bye: ${data.message}`);
    } catch (error) {
      console.error("Error calling /goodbye/bye endpoint:", error);
      setApiResponse("An error occurred calling /goodbye/bye endpoint");
    }
  }

  async function callSeeyaApi() {
    try {
      const token = await getToken();
      const res = await fetch(`${apiUrl}/goodbye/seeya`, {
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
      });
      const data = await res.json();
      console.log("Goodbye Seeya API Response:", data);
      setApiResponse(`Goodbye Seeya: ${data.message}`);
    } catch (error) {
      console.error("Error calling /goodbye/seeya endpoint:", error);
      setApiResponse("An error occurred calling /goodbye/seeya endpoint");
    }
  }

  return (
    <div className="flex flex-col gap-4 items-center w-full">
      <Button onClick={callHelloApi}>Call /hello Endpoint</Button>
      <Button onClick={callByeApi}>Call /goodbye/bye Endpoint</Button>
      <Button onClick={callSeeyaApi}>Call /goodbye/seeya Endpoint</Button>
      {apiResponse && <p className="mt-4">Response: {apiResponse}</p>}
    </div>
  );
}
