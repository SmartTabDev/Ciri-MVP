"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

const subscriptionData = [
  { month: "Jan", subscriptions: 120, revenue: 2400 },
  { month: "Feb", subscriptions: 180, revenue: 3600 },
  { month: "Mar", subscriptions: 220, revenue: 4400 },
  { month: "Apr", subscriptions: 280, revenue: 5600 },
  { month: "May", subscriptions: 320, revenue: 6400 },
  { month: "Jun", subscriptions: 380, revenue: 7600 },
  { month: "Jul", subscriptions: 420, revenue: 8400 },
  { month: "Aug", subscriptions: 480, revenue: 9600 },
  { month: "Sep", subscriptions: 520, revenue: 10400 },
  { month: "Oct", subscriptions: 580, revenue: 11600 },
  { month: "Nov", subscriptions: 640, revenue: 12800 },
  { month: "Dec", subscriptions: 720, revenue: 14400 },
];

const chartConfig = {
  subscriptions: {
    label: "Subscriptions",
    color: "var(--chart-1)",
  },
  revenue: {
    label: "Revenue",
    color: "var(--chart-2)",
  },
} satisfies ChartConfig;

export function SubscriptionPanel() {
  const totalSubscriptions = subscriptionData[subscriptionData.length - 1].subscriptions;
  const totalRevenue = subscriptionData[subscriptionData.length - 1].revenue;
  const growthRate = ((totalSubscriptions - subscriptionData[subscriptionData.length - 2].subscriptions) / subscriptionData[subscriptionData.length - 2].subscriptions * 100).toFixed(1);

  return (
    <Card className="h-full relative overflow-hidden">
      <CardHeader>
        <CardTitle>Subscription Growth</CardTitle>
        <CardDescription>
          Track your subscription growth and revenue over time
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <div className="text-2xl font-bold">{totalSubscriptions.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">Total Subscriptions</p>
            </div>
            <div>
              <div className="text-2xl font-bold">${totalRevenue.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">Total Revenue</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm text-muted-foreground">Growth Rate:</span>
            <span className={`text-sm font-medium ${parseFloat(growthRate) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {parseFloat(growthRate) >= 0 ? '+' : ''}{growthRate}%
            </span>
          </div>

          <ChartContainer className="h-[300px] w-full" config={chartConfig}>
            <LineChart
              data={subscriptionData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <XAxis 
                dataKey="month" 
                axisLine={false}
                tickLine={false}
                className="text-xs"
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                className="text-xs"
              />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    indicator="line"
                    formatter={(value, name) => [
                      name === 'subscriptions' ? `${value} subs` : `$${value}`,
                      name === 'subscriptions' ? 'Subscriptions' : 'Revenue'
                    ]}
                  />
                }
              />
              <Line
                type="monotone"
                dataKey="subscriptions"
                stroke="var(--color-subscriptions)"
                strokeWidth={2}
                dot={{ fill: "var(--color-subscriptions)", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, strokeWidth: 2 }}
              />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="var(--color-revenue)"
                strokeWidth={2}
                dot={{ fill: "var(--color-revenue)", strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, strokeWidth: 2 }}
              />
            </LineChart>
          </ChartContainer>
        </div>
      </CardContent>
      
      {/* Blur Overlay */}
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm flex items-center justify-center z-10">
        <div className="text-center">
          <div className="text-2xl font-bold text-muted-foreground mb-2">Coming Soon...</div>
          <div className="text-sm text-muted-foreground">Subscription analytics will be available soon</div>
        </div>
      </div>
    </Card>
  );
} 