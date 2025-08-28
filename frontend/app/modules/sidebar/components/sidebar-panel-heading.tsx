import type { ComponentPropsWithoutRef } from "react";

import { cn } from "@/lib/utils";

type SidebarPanelHeadingProps = Readonly<ComponentPropsWithoutRef<"div">>;

export default function SidebarPanelHeading({
  children,
  className,
  ...props
}: SidebarPanelHeadingProps) {
  return (
    <div
      className={cn(
        "border-[var(--border)] bg-[var(--muted)]/80 text-[var(--muted-foreground)] flex h-10 shrink-0 items-center gap-x-2 border-b px-4 text-center text-sm leading-none font-semibold select-none",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
