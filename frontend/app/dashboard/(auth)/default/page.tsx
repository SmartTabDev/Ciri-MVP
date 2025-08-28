import { generateMeta } from "@/lib/utils";

import CustomDateRangePicker from "@/components/custom-date-range-picker";
import { DashboardProvider } from "@/dashboard/(auth)/default/context/dashboard-context";

import {
  AIHandledRequestsCard,
  AverageResponseTimeCard,
  HumanEscalationRateCard,
  CustomerSatisfactionCard,
  SubscriptionPanel,
  CalendarPanel,
  OrderStatusPanel,
  LeadBySourcePanel,
} from "@/dashboard/(auth)/default/components";

export async function generateMetadata() {
  return generateMeta({
    title: "Admin Dashboard",
    description:
      "The admin dashboard template offers a sleek and efficient interface for monitoring important data and user interactions. Built with shadcn/ui.",
    canonical: "/default",
  });
}

function DashboardContent() {
  return (
    <div className="space-y-4">
      <div className="flex flex-row items-center justify-between">
        <h1 className="text-xl font-bold tracking-tight lg:text-2xl">
          Dashboard
        </h1>
        <div className="flex items-center space-x-2">
          <CustomDateRangePicker />
        </div>
      </div>
      
      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <AIHandledRequestsCard />
        <AverageResponseTimeCard />
        <HumanEscalationRateCard />
        <CustomerSatisfactionCard />
      </div>

      {/* Main Dashboard Panels - Row 1 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
        <SubscriptionPanel />
        <CalendarPanel />
      </div>

      {/* Main Dashboard Panels - Row 2 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2">
        <OrderStatusPanel />
        <LeadBySourcePanel />
      </div>
    </div>
  );
}

export default function Page() {
  return (
    <DashboardProvider>
      <DashboardContent />
    </DashboardProvider>
  );
}
