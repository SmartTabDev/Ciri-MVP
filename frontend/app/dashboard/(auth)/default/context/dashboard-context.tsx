"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { DateRange } from "react-day-picker";
import { startOfDay, subDays, endOfDay } from "date-fns";
import axios from "axios";

interface AnalyticsData {
  aiHandledRequests: number;
  percentageChange: number;
  averageResponseTime: string;
  humanEscalationRate: number;
  customerSatisfaction: number;
  dateRange: {
    startDate: string;
    endDate: string;
  };
}

interface DashboardContextType {
  dateRange: DateRange | undefined;
  setDateRange: (range: DateRange | undefined) => void;
  analyticsData: AnalyticsData | null;
  loading: boolean;
  error: string | null;
  refreshAnalytics: () => void;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export function useDashboard() {
  const context = useContext(DashboardContext);
  if (context === undefined) {
    throw new Error("useDashboard must be used within a DashboardProvider");
  }
  return context;
}

interface DashboardProviderProps {
  children: ReactNode;
}

export function DashboardProvider({ children }: DashboardProviderProps) {
  const [dateRange, setDateRange] = useState<DateRange | undefined>({
    from: startOfDay(subDays(new Date(), 27)),
    to: endOfDay(new Date()),
  });
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async (range: DateRange | undefined) => {
    if (!range?.from || !range?.to) return;

    setLoading(true);
    setError(null);

    try {
      // Get access token from localStorage
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;

      // Set from date to start of day (00:00:00) and to date to end of day (23:59:59)
      const fromDate = startOfDay(range.from);
      const toDate = endOfDay(range.to);

      // Call the backend analytics API using axios
      const response = await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/v1/analytics/ai-handled-requests`,
        {
          startDate: fromDate.toISOString(),
          endDate: toDate.toISOString(),
        },
        {
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(refreshToken ? { "X-Refresh-Token": refreshToken } : {}),
          },
          withCredentials: true, // Include cookies for authentication
        }
      );

      if (response.data.success) {
        setAnalyticsData(response.data.data);
      } else {
        throw new Error(response.data.error || "Failed to fetch analytics data");
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || "An error occurred";
      setError(errorMessage);
      console.error("Error fetching analytics:", err);
    } finally {
      setLoading(false);
    }
  };

  const refreshAnalytics = () => {
    fetchAnalytics(dateRange);
  };

  // Fetch analytics when date range changes
  useEffect(() => {
    fetchAnalytics(dateRange);
  }, [dateRange]);

  const value: DashboardContextType = {
    dateRange,
    setDateRange,
    analyticsData,
    loading,
    error,
    refreshAnalytics,
  };

  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
} 