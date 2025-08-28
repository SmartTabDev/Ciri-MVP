import type { ComponentPropsWithoutRef } from "react";

import { cn } from "@/lib/utils";

type CustomControlButtonProps = Readonly<ComponentPropsWithoutRef<"button">>;

export default function CustomControlButton({
  children,
  className,
  ...props
}: CustomControlButtonProps) {
  return (
    <button
      type="button"
      className={cn(
        "disabled:pointer-events-none disabled:opacity-30 disabled:cursor-not-allowed text-[var(--primary)] bg-[var(--primary-foreground)] hover:bg-[var(--secondary)] hover:text-[var(--secondary-foreground)] active:bg-[var(--muted)] flex size-7 items-center justify-center rounded-md border-none transition",
        className,
      )}
      {...props}
    >
      {children}
    </button>
  );
}
