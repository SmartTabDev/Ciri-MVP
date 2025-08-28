import { type DragEvent, type ReactNode, useCallback } from "react";

import type { useInsertNode } from "@/modules/flow-builder/hooks/use-insert-node";
import type { BuilderNodeType } from "@/modules/nodes/types";
import type { ApplicationState } from "@/stores/application-state";

import { NODE_TYPE_DRAG_DATA_FORMAT } from "@/constants/symbols";

import { cn } from "@/lib/utils";
import Icon from "@/components/icon-component";

type NodePreviewDraggableProps = Readonly<{
  icon: string | ReactNode;
  title: string;
  description: string;
  type: string;
  children?: never;
  isMobileView: boolean;
  setActivePanel: (panel: ApplicationState["sidebar"]["active"]) => void;
  insertNode: ReturnType<typeof useInsertNode>;
}>;

export function NodePreviewDraggable({
  icon,
  title,
  description,
  type,
  isMobileView,
  setActivePanel,
  insertNode,
}: NodePreviewDraggableProps) {
  const onDragStart = useCallback(
    (e: DragEvent, type: string) => {
      if (isMobileView) return;

      e.dataTransfer.setData(NODE_TYPE_DRAG_DATA_FORMAT, type);
      e.dataTransfer.effectAllowed = "move";
    },
    [isMobileView],
  );

  const onClick = useCallback(() => {
    if (!isMobileView) return;

    insertNode(type as BuilderNodeType);
    setActivePanel("none");
  }, [insertNode, isMobileView, setActivePanel, type]);

  return (
    <div
      className={cn(
        "flex cursor-grab gap-2 rounded-xl border border-neutral-700 bg-[var(--primary-foreground)]! p-2.5 shadow-sm transition select-none hover:ring-2 hover:ring-teal-600/50",
        isMobileView && "active:scale-98 active:opacity-70",
      )}
      onClick={onClick}
      onDragStart={(e) => onDragStart(e, type)}
      draggable
      data-vaul-no-drag
    >
      <div className="shrink-0">
        <div className="flex size-10 items-center justify-center rounded-xl border border-neutral-700 bg-neutral-800">
          {typeof icon === "string" ? (
            <Icon name={icon} className="size-6 text-white" />
          ) : (
            icon
          )}
        </div>
      </div>

      <div className="ml-1 flex grow flex-col">
        <div className="mt-px text-sm leading-normal font-medium text-[var(--text-main)]!">
          {title}
        </div>

        <div className="mt-1 line-clamp-3 text-xs leading-normal text-[var(--text-main)]!">
          {description}
        </div>
      </div>
    </div>
  );
}
