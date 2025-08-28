import { Toaster } from "sonner";

import { useMotherStore } from "@/stores/motherStore";

export function ToasterModule() {
  const [isMobileView] = useMotherStore((s) => [s.view.mobile]);

  return (
    <Toaster
      richColors
      position={isMobileView ? "top-center" : "bottom-center"}
      gap={12}
      closeButton
      toastOptions={{
        classNames: {
          toast:
            "rounded-xl w-full shadow-xl items-start gap-x-2 bg-[var(--background)] text-[var(--foreground)] border border-[var(--border)]",
          title: "text-sm font-medium leading-none text-[var(--foreground)]",
          description: "op-80 leading-snug mt-1 text-[var(--muted-foreground)]",
          icon: "shrink-0",
          success: "border-[var(--success-border)] bg-[var(--success-bg)]",
          error: "border-[var(--error-border)] bg-[var(--error-bg)]",
        },
      }}
    />
  );
}
