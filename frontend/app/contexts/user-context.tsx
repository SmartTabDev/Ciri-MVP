'use client'

import React, { createContext, useState, useContext, ReactNode, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { jwtDecode } from "jwt-decode";
import axios from "axios";
import { getApiUrl } from "@/lib/utils";

export type User = {
  id?: number;
  username?: string;
  email?: string;
  is_verified?: boolean;
  company_id?: number | null;
  [key: string]: any;
};

export const UserContext = createContext<{
  user: User | null;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
  loading: boolean;
  error: string | null;
  isAuthenticated: boolean;
  logout: () => void;
} | undefined>(undefined);

function isTokenExpired(token: string): boolean {
  try {
    const decoded: any = jwtDecode(token);
    if (!decoded.exp) return true;
    return decoded.exp * 1000 < Date.now();
  } catch {
    return true;
  }
}

async function fetchUserInfo(token: string) {
  const res = await axios.get(getApiUrl() + "/v1/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
  return res.data;
}

async function refreshAccessToken(refreshToken: string) {
  const res = await axios.post(getApiUrl() + "/v1/auth/refresh", {
    refresh_token: refreshToken,
  });
  return res.data;
}

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_info");
    setUser(null);
    setIsAuthenticated(false);
    router.replace("/login");
  };

  useEffect(() => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("access_token");
      const refreshToken = localStorage.getItem("refresh_token");
      
      const handleAuth = async () => {
        setLoading(true);
        setError(null);
        
        // Skip auth check for public routes
        if (pathname.startsWith("/login") || 
            pathname.startsWith("/signup") || 
            pathname.startsWith("/forgot-password") || 
            pathname.startsWith("/reset-password") ||
            pathname.startsWith("/verify-code")) {
          setLoading(false);
          return;
        }

        let validToken = token;
        
        if (!token) {
          setIsAuthenticated(false);
          router.replace("/login");
          setLoading(false);
          return;
        }

        // Check if token is expired and refresh if needed
        if (isTokenExpired(token)) {
          if (!refreshToken) {
            setIsAuthenticated(false);
            router.replace("/login");
            setLoading(false);
            return;
          }
          
          try {
            const refreshed = await refreshAccessToken(refreshToken);
            localStorage.setItem("access_token", refreshed.access_token);
            localStorage.setItem("refresh_token", refreshed.refresh_token);
            validToken = refreshed.access_token;
          } catch (err) {
            setError("Session expired. Please login again.");
            setIsAuthenticated(false);
            router.replace("/login");
            setLoading(false);
            return;
          }
        }

        // Fetch user info with valid token
        try {
          const userInfo = await fetchUserInfo(validToken!);
          setUser(userInfo);
          setIsAuthenticated(true);
          
          // Store user info in localStorage for other contexts
          localStorage.setItem("user_info", JSON.stringify(userInfo));

          // Handle unverified users
          if (userInfo && userInfo.is_verified === false) {
            router.replace(
              `/verify-code${userInfo.email ? `?email=${encodeURIComponent(userInfo.email)}` : ""}`,
            );
            setLoading(false);
            return;
          }

          // Handle onboarding for users without company
          if (userInfo && (userInfo.company_id === null || userInfo.company_id === undefined)) {
            router.replace("/onboarding");
            setLoading(false);
            return;
          }

        } catch (err: any) {
          setError(err.message || "Failed to fetch user information");
          setIsAuthenticated(false);
          router.replace("/login");
          setLoading(false);
          return;
        }
        
        setLoading(false);
      };

      handleAuth();
    }
  }, [router, pathname]);

  return (
    <UserContext.Provider value={{ user, setUser, loading, error, isAuthenticated, logout }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
}; 