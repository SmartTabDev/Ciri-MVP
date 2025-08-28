"use client";

import { Label } from "@/components/ui/label";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { useSidebar } from "@/components/ui/sidebar";

export function SidebarModeSelector() {
  const { toggleSidebar } = useSidebar();

  return (
    <div className="hidden flex-col gap-4 lg:flex">
      <Label>Navigasjon modus:</Label>
      <ToggleGroup
        type="single"
        onValueChange={() => toggleSidebar()}
        className="*:border-input w-full gap-4 *:rounded-md *:border"
      >
        <ToggleGroupItem variant="outline" value="full">
          Standard
        </ToggleGroupItem>
        <ToggleGroupItem
          variant="outline"
          value="centered"
          className="data-[variant=outline]:border-l-1"
        >
          Lukket
        </ToggleGroupItem>
      </ToggleGroup>
    </div>
  );
}
