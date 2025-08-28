import type { ComponentPropsWithoutRef } from "react";

import { cn } from "@/lib/utils";

export function SocialButtonLink({
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<"a">) {
  return (
    <a
      target="_blank"
      className={cn(
        "active:border-[var(--border)] active:bg-[var(--muted)] hover:bg-[var(--muted-foreground)] flex size-9 cursor-pointer items-center justify-center gap-x-2 rounded-lg border border-transparent bg-transparent text-sm transition text-[var(--primary)]",
        className,
      )}
      {...props}
    >
      {children}
    </a>
  );
}
