import React from "react";

const FancyTitle = () => {
  return (
    <div className="w-full flex justify-center items-center my-8">
      <h1 className="text-4xl md:text-5xl font-bold">
        <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 from-10% via-blue-600 via-30% via-purple-700 via-70% to-pink-600 to-90% animate-gradient-x">
          LLM Student Advisor
        </span>
      </h1>
    </div>
  );
};

const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes gradient-x {
    0% { background-position: 0% 50%; }
    100% { background-position: 100% 50%; }
  }
  
  .animate-gradient-x {
    background-size: 400% 100%;
    animation: gradient-x 3s linear infinite alternate;
  }
`;
document.head.appendChild(styleSheet);

export default FancyTitle;
