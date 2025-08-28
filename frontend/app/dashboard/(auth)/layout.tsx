"use client";

import React from "react";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import Sidebar from "@/components/layout/sidebar";
import Header from "@/components/layout/header";
import { Toaster } from "@/components/ui/sonner";
import { useUser } from "@/contexts/user-context";

export default function AuthLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const { loading, isAuthenticated, user } = useUser();

  // Show loading state while authentication is being checked
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <span className="text-black">Checking authentication...</span>
        </div>
      </div>
    );
  }

  // Don't render anything if user is not authenticated
  // The user context will handle redirects
  if (!isAuthenticated || !user?.company_id) {
    return null;
  }

  return (
    <SidebarProvider defaultOpen={true}>
      <Sidebar />
      <SidebarInset>
        <Header />
        <div className="@container/main p-4 xl:group-data-[theme-content-layout=centered]/layout:container xl:group-data-[theme-content-layout=centered]/layout:mx-auto xl:group-data-[theme-content-layout=centered]/layout:mt-8">
          {children}
        </div>
        <Toaster position="top-center" />
      </SidebarInset>
    </SidebarProvider>
  );
}
