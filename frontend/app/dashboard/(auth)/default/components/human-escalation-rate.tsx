"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { UserCheck, Loader2 } from "lucide-react";
import { useDashboard } from "@/dashboard/(auth)/default/context/dashboard-context";

export function HumanEscalationRateCard() {
  const { analyticsData, loading, error } = useDashboard();

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Eskalert til menneske
          </CardTitle>
          <UserCheck className="text-muted-foreground h-4 w-4" />
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
            Eskalert til menneske
          </CardTitle>
          <UserCheck className="text-muted-foreground h-4 w-4" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">--</div>
          <p className="text-muted-foreground text-xs">
            <span className="text-red-600">Feil med innlasting av data</span>
          </p>
        </CardContent>
      </Card>
    );
  }

  const escalationRate = analyticsData?.humanEscalationRate || 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Eskalert til menneske
        </CardTitle>
        <UserCheck className="text-muted-foreground h-4 w-4" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{escalationRate}%</div>
        <p className="text-muted-foreground text-xs">
          Forespørsler eskalert til menneske
        </p>
      </CardContent>
    </Card>
  );
}
