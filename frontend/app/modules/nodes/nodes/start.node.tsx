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

export interface StartNodeData extends BaseNodeData {
  label?: string;
  sourceHandleId?: string; // Add stable handle ID
}

const NODE_TYPE = BuilderNode.START;

// eslint-disable-next-line react-refresh/only-export-components
export const metadata: RegisterNodeMetadata<StartNodeData> = {
  type: NODE_TYPE,
  node: memo(StartNode),
  detail: {
    icon: "mynaui:play",
    title: "Start",
    description: "Start the chatbot flow",
  },
  available: false,
  defaultData: {
    label: "Start",
    deletable: false,
  },
};

console.log("Start node metadata: ", metadata);

NODE_REGISTRY.set(metadata.type, metadata);

type StartNodeProps = NodeProps<Node<StartNodeData, typeof NODE_TYPE>>;

export function StartNode({ data, selected, isConnectable }: StartNodeProps) {
  const meta = metadata.detail;

  console.log("Start node reached");

  // Use stable handle ID from data or generate one
  const [sourceHandleId] = useState<string>(() => {
    if (data.sourceHandleId) {
      return data.sourceHandleId;
    }
    return nanoid();
  });

  // Update data with the handle ID if it doesn't exist
  useEffect(() => {
    if (!data.sourceHandleId) {
      data.sourceHandleId = sourceHandleId;
    }
  }, [data, sourceHandleId]);

  return (
    <>
      <div
        data-selected={selected}
        className="border-dark-100 bg-dark-300 data-[selected=true]:(border-teal-600 ring-teal-600/50) flex items-center rounded-full border px-4 py-2 text-[var(--primary)] shadow-sm ring-1 transition dark:text-white"
      >
        <Icon
          name={meta.icon ?? ""}
          className="mr-2 size-4.5 shrink-0 scale-130"
        />

        <span className="mr-1">{meta.title}</span>
      </div>

      <CustomHandle
        type="source"
        id={sourceHandleId}
        position={Position.Right}
        isConnectable={isConnectable}
      />
    </>
  );
}
