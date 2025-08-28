"use client";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";

import { cn } from "@/lib/utils";
import Icon from "@/components/icon-component";
import { ConditionalProps } from "../conditional-path.node";
import { useEffect, useState } from "react";

type ConditionDropdownSelectorProps = Readonly<{
  onChange: (value: { id: string; label: string } | null) => void;
  conditionsList: ConditionalProps;
  value?: { id: string; label: string } | null;
}>;

export function ConditionDropdownSelector({
  onChange,
  conditionsList,
  value,
}: ConditionDropdownSelectorProps) {
  const [label, setLabel] = useState<string>(
    value?.label ?? "Legg til en kategori",
  );

  useEffect(() => {
    if (value?.label) {
      setLabel(value.label);
    }
  }, [value]);

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          type="button"
          className="flex h-8 w-full items-center justify-between rounded-md border border-[var(--border)] bg-[var(--muted)] px-2.5 transition outline-none active:border-[var(--border)] active:bg-[var(--muted)]/50 data-[state=closed]:hover:bg-[var(--muted)] data-[state=open]:border-[var(--border)] data-[state=open]:bg-[var(--background)]"
        >
          <div className="flex items-center">
            <div className="text-sm leading-none font-medium tracking-wide dark:text-white">
              {label}
            </div>
          </div>

          <Icon
            name="lucide:chevrons-up-down"
            className="op-50 ml-1 size-3 dark:text-white"
          />
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          align="start"
          sideOffset={5}
          className={cn(
            "min-w-40 rounded-lg border border-[var(--border)] bg-[var(--muted)]/90 p-0.5 text-[var(--foreground)] shadow-xl backdrop-blur-lg transition select-none dark:text-white",
            "animate-in data-[side=top]:slide-in-bottom-0.5 data-[side=bottom]:slide-in-bottom--0.5 data-[side=bottom]:fade-in-40 data-[side=top]:fade-in-40",
          )}
        >
          {conditionsList.map(({ id, label }) => (
            <DropdownMenu.Item
              key={id}
              className="flex h-8 cursor-pointer items-center rounded-lg border border-transparent p-1.5 pr-6 transition outline-none hover:bg-[var(--background)] active:border-[var(--border)] active:bg-[var(--muted)]"
              onSelect={() => {
                onChange({ id, label });
                setLabel(label);
              }}
            >
              <div className="flex items-center gap-x-2">
                <div className="text-xs leading-none font-medium tracking-wide dark:text-white">
                  {label}
                </div>
              </div>
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
