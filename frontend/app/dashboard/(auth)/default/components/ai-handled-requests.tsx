"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Loader2 } from "lucide-react";
import { useDashboard } from "@/dashboard/(auth)/default/context/dashboard-context";

export function AIHandledRequestsCard() {
  const { analyticsData, loading, error } = useDashboard();

  const formatNumber = (num: number) => {
    return num.toLocaleString();
  };

  const getTrendIcon = (percentageChange: number) => {
    if (percentageChange > 0) {
      return <TrendingUp className="h-4 w-4 text-green-600" />;
    } else if (percentageChange < 0) {
      return <TrendingDown className="h-4 w-4 text-red-600" />;
    }
    return <TrendingUp className="text-muted-foreground h-4 w-4" />;
  };

  const getTrendColor = (percentageChange: number) => {
    if (percentageChange > 0) {
      return "text-green-600";
    } else if (percentageChange < 0) {
      return "text-red-600";
    }
    return "text-muted-foreground";
  };

  const getTrendText = (percentageChange: number) => {
    const absValue = Math.abs(percentageChange);
    const sign = percentageChange > 0 ? "+" : percentageChange < 0 ? "-" : "";
    return `${sign}${absValue.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Ciri-håndterte forespørsler
          </CardTitle>
          <Loader2 className="text-muted-foreground h-4 w-4 animate-spin" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">...</div>
          <p className="text-muted-foreground text-xs">Laster inn...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Ciri-håndterte forespørsler
          </CardTitle>
          <TrendingUp className="text-muted-foreground h-4 w-4" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">-</div>
          <p className="text-xs text-red-600">Feil ved innlasting av data</p>
        </CardContent>
      </Card>
    );
  }

  const requests = analyticsData?.aiHandledRequests || 0;
  const percentageChange = analyticsData?.percentageChange || 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Ciri-håndterte forespørsler
        </CardTitle>
        {getTrendIcon(percentageChange)}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{formatNumber(requests)}</div>
        <p className="text-muted-foreground text-xs">
          <span className={getTrendColor(percentageChange)}>
            {getTrendText(percentageChange)}
          </span>{" "}
          fra sist periode
        </p>
      </CardContent>
    </Card>
  );
}
