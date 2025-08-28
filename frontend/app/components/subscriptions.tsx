"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Bar, BarChart, LabelList, Sector } from "recharts";
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import React from "react";

//todo the data needs to be the total incoming trafic from all channels daily
const chartData = [
  {
    revenue: 10400,
    subscription: 240,
  },
  {
    revenue: 14405,
    subscription: 300,
  },
  {
    revenue: 9400,
    subscription: 200,
  },
  {
    revenue: 8200,
    subscription: 278,
  },
  {
    revenue: 7000,
    subscription: 189,
  },
  {
    revenue: 9600,
    subscription: 239,
  },
  {
    revenue: 11244,
    subscription: 278,
  },
  {
    revenue: 26475,
    subscription: 189,
  },
];

const chartConfig = {
  desktop: {
    label: "Subscription",
    color: "var(--primary)",
  },
} satisfies ChartConfig;

export function SubscriptionsCard() {
  const [activeIndex, setActiveIndex] = React.useState(-1);
  return (
    <Card className="h-full content-center">
      <CardHeader>
        <CardTitle>Trafikk</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="font-display text-3xl leading-6">+4850</div>
        <p className="text-muted-foreground mt-1.5 text-xs">
          <span className="text-green-500">+180.1%</span> from last month
        </p>
        <ChartContainer className="mt-6 h-[200px] w-full" config={chartConfig}>
          <BarChart
            margin={{
              top: 22,
              right: 0,
              left: 0,
            }}
            accessibilityLayer
            data={chartData}
          >
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Bar
              dataKey="subscription"
              fill="var(--color-desktop)"
              radius={5}
              onMouseEnter={(_, index) => setActiveIndex(index)}
              onMouseLeave={() => setActiveIndex(-1)}
              activeBar={(props: any) => {
                const { x, y, width, height, fill } = props;
                return (
                  <rect
                    x={x}
                    y={y}
                    width={width}
                    height={height + 10}
                    rx={8} // Increased radius for the hovered bar
                    ry={20} // Increased radius for the hovered bar
                    fill={fill}
                  />
                );
              }}
            >
              <LabelList
                position="top"
                offset={12}
                className="fill-foreground"
                fontSize={12}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
}
