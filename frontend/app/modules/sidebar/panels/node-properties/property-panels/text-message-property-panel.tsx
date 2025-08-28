import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import { listify } from "radash";
import { useMemo } from "react";

import type { TextMessageNodeData } from "@/modules/nodes/nodes/text-message-node/text-message.node";
import type { BuilderNodeType } from "@/modules/nodes/types";

import { MessageChannelDetails } from "@/modules/nodes/nodes/text-message-node/constants/channels";

import { cn } from "@/lib/utils";
import Icon from "@/components/icon-component";

type TextMessageNodePropertyPanelProps = Readonly<{
  id: string;
  type: BuilderNodeType;
  data: TextMessageNodeData;
  updateData: (data: Partial<TextMessageNodeData>) => void;
}>;

export default function TextMessageNodePropertyPanel({
  id,
  data,
  updateData,
}: TextMessageNodePropertyPanelProps) {
  const currentMessageChannelDetail = useMemo(() => {
    return MessageChannelDetails[
      data.channel as keyof typeof MessageChannelDetails
    ];
  }, [data.channel]);

  return (
    <div className="flex flex-col gap-4.5 p-4">
      {/* <div className="flex flex-col">
        <div className="text-[var(--muted-foreground)]/60 text-xs font-semibold">
          Unique Identifier
        </div>

        <div className="mt-2 flex">
          <input
            type="text"
            value={id}
            readOnly
            className="border-[var(--border)] bg-[var(--muted)] hover:bg-[var(--muted-foreground)]/60 read-only:text-[var(--muted-foreground)]/80 read-only:opacity-80 read-only:hover:bg-[var(--muted-foreground)]/30 h-8 w-full rounded-md border px-2.5 text-sm font-medium shadow-sm transition outline-none"
          />
        </div>
      </div> */}

      <div className="flex flex-col">
        <div className="text-xs font-semibold text-[var(--muted-foreground)]/60">
          Type
        </div>

        <div className="mt-2 flex">
          <DropdownMenu.Root>
            <DropdownMenu.Trigger asChild>
              <button
                type="button"
                className="flex h-8 w-full items-center justify-between rounded-md border border-[var(--border)] bg-[var(--muted)] px-2.5 shadow-sm transition outline-none active:border-[var(--border)] active:bg-[var(--muted)]/50 data-[state=closed]:hover:bg-[var(--muted-foreground)]/60 data-[state=open]:border-[var(--border)] data-[state=open]:bg-[var(--background)]"
              >
                <div className="flex items-center dark:text-white">
                  <Icon
                    name={currentMessageChannelDetail.icon}
                    className="size-4"
                  />

                  <div className="ml-2 text-sm leading-none font-medium tracking-wide">
                    {currentMessageChannelDetail.name}
                  </div>
                </div>

                <Icon
                  name="lucide:chevrons-up-down"
                  className="op-50 ml-1 size-3"
                />
              </button>
            </DropdownMenu.Trigger>

            <DropdownMenu.Portal>
              <DropdownMenu.Content
                sideOffset={5}
                align="start"
                className={cn(
                  "[width:var(--radix-popper-anchor-width)] rounded-lg border border-[var(--border)] bg-[var(--muted)]/90 p-0.5 text-[var(--foreground)] shadow-xl backdrop-blur-lg transition select-none",
                  "animate-in data-[side=top]:slide-in-bottom-0.5 data-[side=bottom]:slide-in-bottom--0.5 data-[side=bottom]:fade-in-40 data-[side=top]:fade-in-40",
                )}
              >
                {listify(MessageChannelDetails, (k, v) => (
                  <DropdownMenu.Item
                    key={k}
                    className="cursor-pointer rounded-lg border border-transparent p-1.5 transition outline-none hover:bg-[var(--muted)] active:border-[var(--border)] active:bg-[var(--muted)]/60"
                    onSelect={() => updateData({ channel: k })}
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
        </div>
      </div>

      <div className="flex flex-col">
        <div className="text-xs font-semibold text-[var(--muted-foreground)]/60">
          Instruks
        </div>

        <div className="mt-2 flex">
          <textarea
            value={data.message}
            onChange={(e) => updateData({ message: e.target.value })}
            placeholder="Skriv inn instruksen her. . ."
            className="min-h-30 w-full resize-none rounded-md border border-[var(--border)] bg-[var(--muted)] px-2.5 py-2 text-sm font-normal shadow-sm ring-2 transition outline-none placeholder:text-[var(--muted-foreground)]/50 placeholder:italic read-only:text-[var(--muted-foreground)]/80 hover:bg-[var(--muted-foreground)]/60 focus:border-[var(--primary)] focus:bg-[var(--background)] focus:ring-[var(--primary)]/50"
          />
        </div>
      </div>
    </div>
  );
}
