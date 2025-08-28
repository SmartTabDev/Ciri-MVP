"use client";
import { Position } from "@xyflow/react";

import CustomHandle from "@/modules/flow-builder/components/handles/custom-handle";
import Icon from "@/components/icon-component";

type NodePathProps = Readonly<{
  id: string;
  path: { id: string; value: string };
  onRemove: (id: string) => void;
  isConnectable: boolean;
}>;

export function NodePath({ id, onRemove, isConnectable, path }: NodePathProps) {
  return (
    <div className="relative -mx-4 flex h-10 items-center gap-x-2 px-4">
      <div className="flex shrink-0 items-center gap-x-0.5">
        <button
          type="button"
          className="flex size-8 items-center justify-center rounded-md border border-[var(--border)] bg-transparent text-[var(--destructive)] transition outline-none hover:bg-[var(--background)] active:border-[var(--border)] active:bg-[var(--muted)]/50"
          onClick={() => onRemove(id)}
        >
          <Icon name="mynaui:trash" className="size-4" />
        </button>
      </div>

      <input className="w-full" type="text" disabled value={path.value} />

      <CustomHandle
        type="source"
        id={id}
        position={Position.Right}
        isConnectable={isConnectable}
        className="top-5! hover:!ring-2 hover:!ring-[var(--secondary)]/50"
      />
    </div>
  );
}
