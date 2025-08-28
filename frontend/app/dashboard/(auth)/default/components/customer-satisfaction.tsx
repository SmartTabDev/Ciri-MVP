"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Star, Loader2 } from "lucide-react";
import { useDashboard } from "@/dashboard/(auth)/default/context/dashboard-context";

export function CustomerSatisfactionCard() {
  const { analyticsData, loading, error } = useDashboard();

  const formatSatisfaction = (score: number) => {
    // Convert 0-100 score to 0-5 scale
    const rating = (score / 100) * 5;
    return rating.toFixed(1);
  };

  const getSatisfactionColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Kundetilfredshet
          </CardTitle>
          <Star className="text-muted-foreground h-4 w-4" />
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-muted-foreground text-sm">Laster inn...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Kundetilfredshet
          </CardTitle>
          <Star className="text-muted-foreground h-4 w-4" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">--</div>
          <p className="text-muted-foreground text-xs">
            <span className="text-red-600">Feil ved innlasting av data</span>
          </p>
        </CardContent>
      </Card>
    );
  }

  const satisfaction = analyticsData?.customerSatisfaction || 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Kundetilfredshet</CardTitle>
        <Star className="text-muted-foreground h-4 w-4" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {formatSatisfaction(satisfaction)}/5
        </div>
        <p className="text-muted-foreground text-xs">
          <span className={getSatisfactionColor(satisfaction)}>
            {satisfaction}% fornøydhetsrate
          </span>
        </p>
      </CardContent>
    </Card>
  );
}
