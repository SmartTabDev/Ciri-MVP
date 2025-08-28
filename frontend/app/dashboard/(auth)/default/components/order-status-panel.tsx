"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Clock, AlertCircle, XCircle } from "lucide-react";

const statusData = [
  {
    status: "Fullført",
    count: 245,
    description: "Completed leads - outbound requests sent and responded to",
    color: "bg-green-500",
    textColor: "text-green-600",
    icon: CheckCircle,
    percentage: 35,
  },
  {
    status: "Pågår",
    count: 189,
    description: "Awaiting response - outbound reach made but no response yet",
    color: "bg-blue-500",
    textColor: "text-blue-600",
    icon: Clock,
    percentage: 27,
  },
  {
    status: "Venter",
    count: 156,
    description: "Awaiting followup - within close timeframe to present time",
    color: "bg-yellow-500",
    textColor: "text-yellow-600",
    icon: AlertCircle,
    percentage: 22,
  },
  {
    status: "Lost",
    count: 108,
    description: "No response over 10 days - outbound requests with no response",
    color: "bg-red-500",
    textColor: "text-red-600",
    icon: XCircle,
    percentage: 16,
  },
];

export function OrderStatusPanel() {
  const totalLeads = statusData.reduce((sum, item) => sum + item.count, 0);

  return (
    <Card className="h-full relative overflow-hidden">
      <CardHeader>
        <CardTitle>Lead Status Overview</CardTitle>
        <CardDescription>
          Track your lead status distribution and follow-up progress
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Total Leads Summary */}
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
            <div>
              <div className="text-2xl font-bold">{totalLeads.toLocaleString()}</div>
              <p className="text-sm text-muted-foreground">Total Leads</p>
            </div>
            <Badge variant="secondary" className="text-sm">
              Active Campaign
            </Badge>
          </div>

          {/* Status Breakdown */}
          <div className="space-y-3">
            {statusData.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.status} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/30 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full ${item.color} bg-opacity-10`}>
                      <Icon className={`h-4 w-4 ${item.textColor}`} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{item.status}</span>
                        <Badge variant="outline" className="text-xs">
                          {item.count}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground max-w-xs">
                        {item.description}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{item.percentage}%</div>
                    <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${item.color} transition-all duration-300`}
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">
                {((statusData[0].count / totalLeads) * 100).toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">Success Rate</p>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">
                {statusData[1].count + statusData[2].count}
              </div>
              <p className="text-xs text-muted-foreground">In Progress</p>
            </div>
          </div>
        </div>
      </CardContent>
      
      {/* Blur Overlay */}
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm flex items-center justify-center z-10">
        <div className="text-center">
          <div className="text-2xl font-bold text-muted-foreground mb-2">Coming Soon...</div>
          <div className="text-sm text-muted-foreground">Lead status tracking will be available soon</div>
        </div>
      </div>
    </Card>
  );
} 