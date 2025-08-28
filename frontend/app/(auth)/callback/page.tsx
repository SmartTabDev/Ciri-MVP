"use client";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");
    if (accessToken && refreshToken) {
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("refresh_token", refreshToken);
      router.replace("/dashboard");
    } else {
      // Optionally handle error or show a message
      router.replace("/login");
    }
  }, [router, searchParams]);

  return (
    <div className="flex justify-center items-center h-screen bg-background">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
        <span className="text-foreground">Signing you in...</span>
      </div>
    </div>
  );
} 