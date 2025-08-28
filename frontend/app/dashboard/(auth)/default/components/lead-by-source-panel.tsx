"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Mail, MessageCircle, Phone, Globe, TrendingUp } from "lucide-react";

const sourceData = [
  {
    source: "Email",
    count: 523,
    percentage: 68,
    color: "bg-blue-500",
    textColor: "text-blue-600",
    icon: Mail,
    trend: "+12%",
    trendDirection: "up",
  },
  {
    source: "Social Media",
    count: 156,
    percentage: 20,
    color: "bg-purple-500",
    textColor: "text-purple-600",
    icon: MessageCircle,
    trend: "+8%",
    trendDirection: "up",
  },
  {
    source: "Phone",
    count: 67,
    percentage: 9,
    color: "bg-green-500",
    textColor: "text-green-600",
    icon: Phone,
    trend: "+5%",
    trendDirection: "up",
  },
  {
    source: "Website",
    count: 23,
    percentage: 3,
    color: "bg-orange-500",
    textColor: "text-orange-600",
    icon: Globe,
    trend: "-2%",
    trendDirection: "down",
  },
];

export function LeadBySourcePanel() {
  const totalLeads = sourceData.reduce((sum, item) => sum + item.count, 0);

  return (
    <Card className="h-full relative overflow-hidden">
      <CardHeader>
        <CardTitle>Leads by Source</CardTitle>
        <CardDescription>
          Track incoming requests by communication channel
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Total Summary */}
          <div className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
            <div>
              <div className="text-2xl font-bold">{totalLeads.toLocaleString()}</div>
              <p className="text-sm text-muted-foreground">Total Incoming Requests</p>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium text-green-600">+15%</span>
            </div>
          </div>

          {/* Source Breakdown */}
          <div className="space-y-3">
            {sourceData.map((item) => {
              const Icon = item.icon;
              return (
                <div key={item.source} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/30 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-full ${item.color} bg-opacity-10`}>
                      <Icon className={`h-4 w-4 ${item.textColor}`} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{item.source}</span>
                        <Badge variant="outline" className="text-xs">
                          {item.count}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-muted-foreground">
                          {item.percentage}% of total
                        </span>
                        <span className={`text-xs font-medium ${
                          item.trendDirection === 'up' ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {item.trend}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">{item.percentage}%</div>
                    <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
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

          {/* Channel Performance */}
          <div className="pt-4 border-t">
            <h4 className="text-sm font-medium mb-3">Channel Performance</h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 bg-green-50 dark:bg-green-950/20 rounded-lg">
                <div className="text-lg font-bold text-green-600">
                  {sourceData[0].count}
                </div>
                <p className="text-xs text-muted-foreground">Primary Channel</p>
                <p className="text-xs text-green-600 font-medium">Email</p>
              </div>
              <div className="text-center p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <div className="text-lg font-bold text-blue-600">
                  {sourceData[1].count}
                </div>
                <p className="text-xs text-muted-foreground">Growing Channel</p>
                <p className="text-xs text-blue-600 font-medium">Social Media</p>
              </div>
            </div>
          </div>

          {/* Future Implementation Note */}
          <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-start gap-2">
              <div className="p-1 rounded-full bg-blue-100 dark:bg-blue-900">
                <Globe className="h-3 w-3 text-blue-600" />
              </div>
              <div>
                <p className="text-xs font-medium text-blue-800 dark:text-blue-200">
                  Future Implementation
                </p>
                <p className="text-xs text-blue-600 dark:text-blue-300">
                  Additional channels like &quot;LinkedIn&quot;, &quot;WhatsApp&quot;, and &quot;SMS&quot; will be added as the system expands.
                </p>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
      
      {/* Blur Overlay */}
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm flex items-center justify-center z-10">
        <div className="text-center">
          <div className="text-2xl font-bold text-muted-foreground mb-2">Coming Soon...</div>
          <div className="text-sm text-muted-foreground">Lead source analytics will be available soon</div>
        </div>
      </div>
    </Card>
  );
} 