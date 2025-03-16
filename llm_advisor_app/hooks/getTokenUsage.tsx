import { useEffect, useState } from "react";

interface TokenUsage {
  alreadyUsedTokenUsage: number;
}

export function useTokenUsage(apiUrl: string, userSub: string, getToken: () => Promise<string | null>) {
  const [tokenUsage, setTokenUsage] = useState<TokenUsage>({ alreadyUsedTokenUsage: 0 });

  useEffect(() => {
    async function fetchTokenUsage() {
        
    if(!userSub) {
        return
    }

      try {
        const params = new URLSearchParams({
            student_id: `STUDENT#${userSub}`,
        });
        const token = await getToken(); // Fetch the authentication token
        const response = await fetch(`${apiUrl}/token-usage?${params.toString()}`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch token usage");
        }

        const data = await response.json();
        setTokenUsage({ alreadyUsedTokenUsage: data.tokens_remaining });
      } catch (error) {
        console.error("Error fetching token usage:", error);
      }
    }

    fetchTokenUsage();
  }, [apiUrl, userSub, getToken]);

  return tokenUsage; // Returns the token usage data
}
