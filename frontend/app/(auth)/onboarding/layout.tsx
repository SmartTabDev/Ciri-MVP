"use client";
import { useUser } from "@/contexts/user-context";

export default function OnboardingAuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { loading, isAuthenticated } = useUser();

  // Show loading while authentication is being checked
  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <span className="text-foreground">Loading...</span>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated - user context will handle redirect
  if (!isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
