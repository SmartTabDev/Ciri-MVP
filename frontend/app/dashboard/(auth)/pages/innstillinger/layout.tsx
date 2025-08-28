import { Separator } from "@/components/ui/separator";
import { SidebarNav } from "./sidebar-nav";
import { generateMeta } from "@/lib/utils";

export async function generateMetadata() {
  return generateMeta({
    title: "Settings Page",
    description:
      "Example of settings page and form created using react-hook-form and Zod validator. Built with Tailwind CSS and React.",
    canonical: "/pages/settings",
  });
}

const sidebarNavItems = [
  {
    title: "Kontekst",
    href: "/dashboard/pages/innstillinger",
  },
  {
    title: "Integrasjoner",
    href: "/dashboard/pages/innstillinger/integrasjoner",
  },
  {
    title: "Leads og oppfølging",
    href: "/dashboard/pages/innstillinger/leads",
  },
  {
    title: "Konto",
    href: "/dashboard/pages/innstillinger/konto",
  },
];

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <div className="mb-6 space-y-0.5">
        <h2 className="font-display text-2xl font-bold tracking-tight">
          Innstillinger
        </h2>
        <p className="text-muted-foreground"></p>
      </div>
      <div className="flex flex-col space-y-8 lg:flex-row lg:space-y-0 lg:space-x-6">
        <div className="flex-1 lg:max-w-2xl">{children}</div>
        <aside className="lg:w-1/5">
          <SidebarNav items={sidebarNavItems} />
        </aside>
      </div>
    </>
  );
}
