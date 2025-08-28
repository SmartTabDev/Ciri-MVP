import { isEmpty } from "radash";

import type { ComponentPropsWithoutRef } from "react";

import { truncateMiddle } from "@/lib/string";

import { cn } from "@/lib/utils";

import Icon from "@/components/icon-component";

type NodeListItemProps = Readonly<
  ComponentPropsWithoutRef<"button"> & {
    icon: string;
    title: string;
    id?: string;
    selected?: boolean;
    pseudoSelected?: boolean;
  }
>;

export function NodeListItem({
  id,
  title,
  className,
  icon,
  selected,
  pseudoSelected,
  ...props
}: NodeListItemProps) {
  return (
    <button
      type="button"
      className={cn(
        "flex h-8 items-center justify-between gap-4 rounded-lg border border-transparent bg-transparent px-2.5 text-sm transition outline-none select-none",
        selected
          ? "border-teal-700 bg-teal-900 text-white"
          : "hover:bg-[var(--secondary)] active:border-neutral-700 active:bg-neutral-800",
        pseudoSelected && !selected && "bg-neutral-800/60",
        className,
      )}
      {...props}
    >
      <div className="flex items-center">
        <Icon name={icon} className="size-4.5" />
        <div className="op-80 ml-2.5 flex items-center text-xs leading-none font-medium tracking-wide uppercase">
          <span className="translate-y-px">{title}</span>
        </div>
      </div>

      {id && !isEmpty(id) && (
        <div className="text-2.5 rounded-md bg-neutral-900 px-2 py-1.5 leading-none font-semibold tracking-wide text-gray-200/80">
          {truncateMiddle(id, 12)}
        </div>
      )}
    </button>
  );
}
