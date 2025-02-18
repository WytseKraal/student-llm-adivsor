"use client";

import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function Home() {
  const [showText, setShowText] = useState(false);

  const handleButtonClick = () => {
    setShowText(!showText);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-8 pb-20 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <Button onClick={handleButtonClick}>Hallo</Button>
      {showText && <p className="text-cyan-800 text-3xl mt-4">I AM CLICKED</p>}
    </div>
  );
}
