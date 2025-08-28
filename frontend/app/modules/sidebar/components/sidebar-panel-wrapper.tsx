import { OverlayScrollbarsComponent } from "overlayscrollbars-react";

import type { ComponentPropsWithoutRef } from "react";

import { defaultOverlayScrollbarsOptions } from "@/lib/overlayscrollbars";

import { cn } from "@/lib/utils";

type SidebarPanelWrapperProps = Readonly<ComponentPropsWithoutRef<"div">>;

export default function SidebarPanelWrapper({
  children,
  className,
  ...props
}: SidebarPanelWrapperProps) {
  return (
    <div className={cn("flex h-full flex-col", className)} {...props}>
      <OverlayScrollbarsComponent
        className="grow"
        defer
        options={defaultOverlayScrollbarsOptions}
      >
        {children}
      </OverlayScrollbarsComponent>
    </div>
  );
}
