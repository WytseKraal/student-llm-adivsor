"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

// Message type definition
interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
}

interface ChatServiceProps {
  apiUrl: string;
  getToken: () => Promise<string | null>;
}

export default function ChatService({ apiUrl, getToken }: ChatServiceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [tokenUsage, setTokenUsage] = useState<{
    total: number;
    prompt: number;
    completion: number;
  }>({ total: 0, prompt: 0, completion: 0 });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (message: string): Promise<string> => {
    try {
      const token = await getToken();
      if (!token) {
        throw new Error("No authentication token available.");
      }

      // Format the conversation history into a context string
      let contextString = "";
      if (messages.length > 0) {
        contextString = messages
          .map((msg) => {
            const role = msg.sender === "user" ? "User" : "Assistant";
            return `${role}: ${msg.content}`;
          })
          .join("\n\n");
        contextString += "\n\n";
      }

      // Add the current message with the context and formatting instruction
      const enhancedMessage = `${contextString}User: ${message}\n\nPlease format your response using markdown for better readability. Consider the entire conversation history above when responding.`;

      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: enhancedMessage }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      const usage = data.usage;
      setTokenUsage((prevUsage) => ({
        total: prevUsage.total + usage.total_tokens,
        prompt: usage.prompt_tokens,
        completion: usage.completion_tokens,
      }));

      return data.response;
    } catch (error) {
      console.error("API call failed:", error);
      throw error;
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const responseText = await sendMessage(input);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: responseText,
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Failed to send message:", error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, something went wrong. Please try again.",
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full shadow-lg">
      <CardHeader className="border-b">
        <CardTitle className="text-lg">Chat Service</CardTitle>
      </CardHeader>

      <ScrollArea className="h-80 p-4">
        <CardContent className="pt-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-64 text-gray-500">
              Send a message to start chatting
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div className="flex items-start max-w-[80%] gap-2">
                    {message.sender === "bot" && (
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-primary text-primary-foreground">
                          B
                        </AvatarFallback>
                      </Avatar>
                    )}

                    <div
                      className={`rounded-lg px-3 py-2 ${
                        message.sender === "user"
                          ? "bg-primary text-primary-foreground"
                          : "bg-muted"
                      }`}
                    >
                      {message.sender === "bot" ? (
                        <div className="prose prose-sm dark:prose-invert">
                          <ReactMarkdown>{message.content}</ReactMarkdown>
                        </div>
                      ) : (
                        <p>{message.content}</p>
                      )}
                      <p className="text-xs opacity-70 mt-1">
                        {message.timestamp.toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>

                    {message.sender === "user" && (
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-zinc-800 text-zinc-50">
                          U
                        </AvatarFallback>
                      </Avatar>
                    )}
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </CardContent>
      </ScrollArea>

      <CardFooter className="border-t p-4 flex flex-col gap-2">
        <div className="text-xs text-gray-500">
          Total token usage (session): {tokenUsage.total} | Last prompt:{" "}
          {tokenUsage.prompt} | Last completion: {tokenUsage.completion}
        </div>

        <form onSubmit={handleSendMessage} className="flex w-full gap-2">
          <Input
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Sending
              </>
            ) : (
              "Send"
            )}
          </Button>
        </form>
      </CardFooter>
    </Card>
  );
}
