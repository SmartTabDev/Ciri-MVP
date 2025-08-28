import React from "react";

interface StepperProps {
  steps: string[];
  currentStep: number;
}

export const Stepper: React.FC<StepperProps> = ({ steps, currentStep }) => {
  return (
    <div className="flex justify-between mb-8">
      {steps.map((_, idx) => (
        <div key={idx} className="flex-1 flex flex-col items-center">
          <div
            className={`rounded-full w-8 h-8 flex items-center justify-center text-white transition-colors duration-200 ${
              idx === currentStep
                ? "bg-primary"
                : idx < currentStep
                ? "bg-green-500"
                : "bg-muted-foreground"
            }`}
          >
            {idx + 1}
          </div>
        </div>
      ))}
    </div>
  );
}; 