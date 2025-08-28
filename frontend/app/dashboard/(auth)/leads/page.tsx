import React from "react";
import { TableOrderStatus } from "@/components";

export default async function page() {
  return (
    <div className="relative">
      <TableOrderStatus dashboard />
      
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
