"use client";

import { type Node, type NodeProps, Position } from "@xyflow/react";
import { nanoid } from "nanoid";
import { memo, useMemo, useState, useEffect } from "react";

import CustomHandle from "@/modules/flow-builder/components/handles/custom-handle";
import {
  type BaseNodeData,
  BuilderNode,
  type RegisterNodeMetadata,
} from "@/modules/nodes/types";
import { NODE_REGISTRY } from "../registry";

import { cn } from "@/lib/utils";
import Icon from "@/components/icon-component";

export interface EndNodeData extends BaseNodeData {
  label?: string;
  targetHandleId?: string; // Add stable handle ID
}

const NODE_TYPE = BuilderNode.END;

type EndNodeProps = NodeProps<Node<EndNodeData, typeof NODE_TYPE>>;

// eslint-disable-next-line react-refresh/only-export-components
export const metadata: RegisterNodeMetadata<EndNodeData> = {
  type: NODE_TYPE,
  node: memo(EndNode),
  detail: {
    icon: "mynaui:stop",
    title: "Slutt",
    description: "End the chatbot flow",
  },
  available: false,
  defaultData: {
    label: "Slutt",
    deletable: false,
  },
};

NODE_REGISTRY.set(metadata.type, metadata);

export function EndNode({ data, selected }: EndNodeProps) {
  const meta = metadata.detail;

  // Use stable handle ID from data or generate one
  const [targetHandleId] = useState<string>(() => {
    if (data.targetHandleId) {
      return data.targetHandleId;
    }
    return nanoid();
  });

  // Update data with the handle ID if it doesn't exist
  useEffect(() => {
    if (!data.targetHandleId) {
      data.targetHandleId = targetHandleId;
    }
  }, [data, targetHandleId]);

  return (
    <>
      <div
        data-selected={selected}
        data-deletable={false}
        className="border-dark-100 bg-dark-300 data-[selected=true]:(border-teal-600 ring-teal-600/50) flex items-center rounded-full border px-4 py-2 text-[var(--primary)] shadow-sm ring-1 transition dark:text-white"
      >
        <Icon
          name={meta.icon ?? ""}
          className="mr-2 size-4.5 shrink-0 scale-130"
        />

        <span className="mr-1">{meta.title}</span>
      </div>

      <CustomHandle
        type="target"
        id={targetHandleId}
        position={Position.Left}
        isConnectable
      />
    </>
  );
}
