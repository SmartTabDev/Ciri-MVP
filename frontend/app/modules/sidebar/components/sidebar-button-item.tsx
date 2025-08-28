import type { ComponentPropsWithoutRef } from "react";

import { cn } from "@/lib/utils";

type SidebarButtonItemProps = Readonly<
  ComponentPropsWithoutRef<"button"> & {
    active?: boolean;
  }
>;

export default function SidebarButtonItem({
  children,
  className,
  active,
  ...props
}: SidebarButtonItemProps) {
  return (
    <button
      type="button"
      className={cn(
        "flex size-8 items-center justify-center rounded-lg transition outline-none cursor-pointer",
        [
          active
            ? "border-[var(--primary)] bg-[var(--primary)] text-[var(--primary-foreground)]"
            : "hover:bg-[var(--muted)] active:bg-[var(--muted-foreground)] active:border-[var(--border)] bg-transparent text-[var(--primary)]",
        ],
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
