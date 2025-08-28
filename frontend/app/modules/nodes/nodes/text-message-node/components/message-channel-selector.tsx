"use client";
import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { listify } from "radash";

import {
  type MessageChannelDetail,
  MessageChannelDetails,
  type MessageChannelType,
} from "@/modules/nodes/nodes/text-message-node/constants/channels";

import { cn } from "@/lib/utils";
import Icon from "@/components/icon-component";

type MessageChannelSelectorProps = Readonly<{
  detail: MessageChannelDetail;
  onSelect: (
    channel: MessageChannelDetail & { type: MessageChannelType },
  ) => void;
}>;

export function MessageChannelSelector({
  detail,
  onSelect,
}: MessageChannelSelectorProps) {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          type="button"
          className="px-1.2 active:border-[var(--border)] active:bg-[var(--muted)]/50 data-[state=open]:border-[var(--border)] data-[state=open]:bg-[var(--background)] data-[state=closed]:hover:bg-[var(--background)] flex h-7 items-center justify-center rounded-lg border border-transparent bg-transparent transition outline-none"
        >
          <Icon name={detail.icon} className="size-4" />

          <Icon name="lucide:chevrons-up-down" className="op-50 ml-1 size-3" />
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          sideOffset={5}
          className={cn(
            "border-[var(--border)] bg-[var(--muted)]/90 text-[var(--foreground)] min-w-40 rounded-lg border p-0.5 shadow-xl backdrop-blur-lg transition select-none",
            "animate-in data-[side=top]:slide-in-bottom-0.5 data-[side=bottom]:slide-in-bottom--0.5 data-[side=bottom]:fade-in-40 data-[side=top]:fade-in-40",
          )}
        >
          {listify(MessageChannelDetails, (k, v) => (
            <DropdownMenu.Item
              key={k}
              className="active:border-[var(--border)] active:bg-[var(--muted)] hover:bg-[var(--background)] cursor-pointer rounded-lg border border-transparent p-1.5 transition outline-none"
              onSelect={() => onSelect({ ...v, type: k })}
            >
              <div className="flex items-center gap-x-2">
                <Icon name={v.icon} className="size-4" />

                <div className="text-xs leading-none font-medium tracking-wide">
                  {v.name}
                </div>
              </div>
            </DropdownMenu.Item>
          ))}
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
