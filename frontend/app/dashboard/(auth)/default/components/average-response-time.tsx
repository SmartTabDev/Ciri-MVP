"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Clock, Loader2 } from "lucide-react";
import { useDashboard } from "@/dashboard/(auth)/default/context/dashboard-context";

export function AverageResponseTimeCard() {
  const { analyticsData, loading, error } = useDashboard();

  if (loading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">
            Gjennomsnittlig svartid
          </CardTitle>
          <Clock className="text-muted-foreground h-4 w-4" />
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
            Gjennomsnittlig svartid
          </CardTitle>
          <Clock className="text-muted-foreground h-4 w-4" />
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

  const responseTime = analyticsData?.averageResponseTime || "0s";

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Gjennomsnittlig svartid
        </CardTitle>
        <Clock className="text-muted-foreground h-4 w-4" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{responseTime}</div>
        <p className="text-muted-foreground text-xs">
          Gjennomsnittlig tid fra forespørsel til svar
        </p>
      </CardContent>
    </Card>
  );
}
