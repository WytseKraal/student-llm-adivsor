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
import { env } from "@/environment";

// Message type definition
interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
  timestamp: Date;
}

// LLM API response type
interface LLMResponse {
  content: string;
  model: string;
  usage: {
    completion_tokens: number;
    prompt_tokens: number;
    total_tokens: number;
  };
  id: string;
}

interface ChatServiceProps {
  apiUrl?: string;
  getToken: () => Promise<string | null>;
}

export default function ChatService({ apiUrl, getToken }: ChatServiceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [tokenUsage, setTokenUsage] = useState<{ total: number }>({ total: 0 });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Use provided apiUrl or default from environment
  const apiEndpoint = apiUrl || `${env.apiUrl}/llm`;

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (userMessage: string): Promise<LLMResponse> => {
    // Get authentication token
    const token = await getToken();
    if (!token) {
      throw new Error("Authentication failed - no token available");
    }

    // Format messages for LLM API
    const apiMessages = messages.map((msg) => ({
      role: msg.sender === "user" ? "user" : "assistant",
      content: msg.content,
    }));

    // Add the current user message
    apiMessages.push({
      role: "user",
      content: userMessage,
    });

    try {
      const response = await fetch(apiEndpoint, {
        method: "POST",
        headers: {
          Authorization: token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "gpt-4o-mini", // Default model, could be made configurable
          messages: apiMessages,
          temperature: 0.7,
          max_tokens: 100,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          `API error: ${response.status} - ${JSON.stringify(errorData)}`
        );
      }

      const data = await response.json();
      return data as LLMResponse;
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
      const llmResponse = await sendMessage(input);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: llmResponse.content,
        sender: "bot",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);

      // Update token usage stats
      setTokenUsage((prev) => ({
        total: prev.total + llmResponse.usage.total_tokens,
      }));

      console.log(
        `LLM Response - Model: ${llmResponse.model}, ID: ${llmResponse.id}`
      );
      console.log(
        `Token Usage - Completion: ${llmResponse.usage.completion_tokens}, Prompt: ${llmResponse.usage.prompt_tokens}, Total: ${llmResponse.usage.total_tokens}`
      );
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
        <CardTitle className="text-lg">AI Assistant</CardTitle>
        {tokenUsage.total > 0 && (
          <p className="text-xs text-muted-foreground">
            Token usage: {tokenUsage.total} tokens
          </p>
        )}
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
                          AI
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
                      <p>{message.content}</p>
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

      <CardFooter className="border-t p-4">
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
