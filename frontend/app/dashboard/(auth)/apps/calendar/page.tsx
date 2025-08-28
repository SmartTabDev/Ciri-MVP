import { generateMeta } from "@/lib/utils";
import React from "react";
import BigCalendar from "@/components/event-calendar/big-calendar";

export async function generateMetadata() {
  return generateMeta({
    title: "Calendar",
    description:
      "Plan your events or tasks in an organized way with the Calendar app template. Built with shadcn/ui, Next.js and Tailwind CSS.",
    canonical: "/apps/calendar",
  });
}

export default function Page() {
  return (
    <div className="w-full relative">
      <BigCalendar />
      
      {/* Blur Overlay */}
      <div className="absolute inset-0 bg-white/60 backdrop-blur-sm flex items-center justify-center z-50">
        <div className="text-center">
          <h2 className="text-2xl font-semibold text-gray-700 mb-2">Coming Soon...</h2>
          <p className="text-gray-500">This feature is under development</p>
        </div>
      </div>
    </div>
  );
}
