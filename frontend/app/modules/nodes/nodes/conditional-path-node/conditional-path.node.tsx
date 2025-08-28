"use client";

import * as DropdownMenu from "@radix-ui/react-dropdown-menu";
import {
  type Node,
  type NodeProps,
  Position,
  useReactFlow,
} from "@xyflow/react";
import { nanoid } from "nanoid";
import { memo, useCallback, useMemo, useState, useEffect } from "react";

import CustomHandle from "@/modules/flow-builder/components/handles/custom-handle";
import { useDeleteNode } from "@/modules/flow-builder/hooks/use-delete-node";
import { useUpdateNodeInternals } from "@xyflow/react";
import { ConditionDropdownSelector } from "@/modules/nodes/nodes/conditional-path-node/components/condition-dropdown-selector";
import { NodePath } from "@/modules/nodes/nodes/conditional-path-node/components/node-path";
import { NODE_REGISTRY } from "../../registry";
import {
  type BaseNodeData,
  BuilderNode,
  type RegisterNodeMetadata,
} from "@/modules/nodes/types";

import { cn } from "@/lib/utils";
import Icon from "@/components/icon-component";
import { createNodeWithDefaultData } from "../../utils";

export type ConditionalProps = Readonly<{
  id: string;
  type: "return_warranty" | "communication_style";
  label: string;
  paths: {
    values: string[];
  };
}>[];

export const caseList: ConditionalProps = [
  {
    id: nanoid(),
    type: "return_warranty",
    label: "Kunde spør om retur & garanti",
    paths: {
      values: [
        "Kunde ønsker å returnere en vare",
        "Kunde har spørsmål knyttet garanti",
        "Andre henvendelser",
      ],
    },
  },
  {
    id: nanoid(),
    type: "communication_style",
    label: "Stil og tone-of-voice",
    paths: {
      values: [
        "Start en samtale på en spesifikk måte",
        "Still spesifikke spørsmål ved samtale-slutt",
        "Bruk av emojier",
        "Kommunikasjonsmåte",
        "Andre kommunikasjonsstrategier",
      ],
    },
  },
];

const NODE_TYPE = BuilderNode.CONDITIONAL_PATH;

// eslint-disable-next-line react-refresh/only-export-components
export const metadata: RegisterNodeMetadata<ConditionalPathNodeData> = {
  type: NODE_TYPE,
  node: memo(ConditionalPathNode),
  detail: {
    icon: "mynaui:git-branch",
    title: "Legg til vilkår",
    description:
      "Legg til vilkår slik at Ciri vet hva hun skal gjøre i spesifikke situasjoner.",
  },
  defaultData: {
    condition: null,
    paths: [],
  },
};

NODE_REGISTRY.set(metadata.type, metadata);

export interface ConditionalPathNodeData extends BaseNodeData {
  condition: { id: string; label: string } | null;
  paths: { id: string; value: string }[];
  sourceHandleId?: string; // Add stable handle ID for source
  targetHandleId?: string; // Add stable handle ID for target
}

type ConditionalPathNodeProps = NodeProps<
  Node<ConditionalPathNodeData, typeof NODE_TYPE>
>;

export function ConditionalPathNode({
  id,
  isConnectable,
  selected,
  data,
}: ConditionalPathNodeProps) {
  const meta = metadata.detail;

  // Use stable handle IDs from data or generate new ones
  const [sourceHandleId] = useState<string>(() => {
    if (data.sourceHandleId) {
      return data.sourceHandleId;
    }
    return nanoid();
  });
  
  const [targetHandleId] = useState<string>(() => {
    if (data.targetHandleId) {
      return data.targetHandleId;
    }
    return nanoid();
  });

  // Update data with handle IDs if they don't exist
  useEffect(() => {
    if (!data.sourceHandleId) {
      data.sourceHandleId = sourceHandleId;
    }
    if (!data.targetHandleId) {
      data.targetHandleId = targetHandleId;
    }
  }, [data, sourceHandleId, targetHandleId]);

  const updateNodeInternals = useUpdateNodeInternals();
  const { setNodes, setEdges } = useReactFlow();
  const deleteNode = useDeleteNode();

  const onConditionChange = useCallback(
    (c: { id: string; label: string } | null) => {
      setNodes((nodes) =>
        nodes.map((n) =>
          n.id === id
            ? {
                ...n,
                data: {
                  condition: c,
                  paths: [],
                },
              }
            : n,
        ),
      );
    },
    [id, setNodes],
  );

  const filteredCaseList = useMemo(() => {
    const alreadyUsed = new Set(data.paths.map((p) => p.value));
    return (
      caseList.find((c) => c.id === data.condition?.id)?.paths.values ?? []
    )
      .filter((v) => !alreadyUsed.has(v))
      .map((v) => ({ id: nanoid(), value: v }));
  }, [data.paths, data.condition]);

  const addNodePath = useCallback(
    (p: { id: string; value: string }) => {
      setNodes((nodes) =>
        nodes.map((n) =>
          n.id === id
            ? {
                ...n,
                data: {
                  ...(n.data as ConditionalPathNodeData),
                  paths: [...(n.data as ConditionalPathNodeData).paths, p],
                },
              }
            : n,
        ),
      );
      updateNodeInternals(id);
    },
    [id, setNodes],
  );

  const removeNodePath = useCallback(
    (pathId: string) => {
      setNodes((nodes) =>
        nodes.map((n) =>
          n.id === id
            ? {
                ...n,
                data: {
                  ...n.data,
                  paths: (
                    n.data.paths as ConditionalPathNodeData["paths"]
                  ).filter((p: { id: string }) => p.id !== pathId),
                },
              }
            : n,
        ),
      );

      setEdges((edges) => edges.filter((edge) => edge.sourceHandle !== pathId));
      updateNodeInternals(id);
    },
    [id, setEdges, setNodes],
  );

  return (
    <div
      data-selected={selected}
      className="w-[400px] divide-y divide-[var(--border)] rounded-xl border border-[var(--border)] bg-[var(--muted)]/50 text-[var(--primary)] shadow-sm ring-1 backdrop-blur-xl transition data-[selected=true]:border-violet-500 data-[selected=true]:ring-violet-500/50"
    >
      <div className="relative overflow-clip rounded-t-xl bg-[var(--muted)]/50">
        <div className="absolute inset-0">
          <div className="from-primary-500/20 absolute h-full w-3/5 bg-gradient-to-r to-transparent" />
        </div>

        <div className="relative flex h-9 items-center justify-between gap-x-4 px-0.5 py-0.5">
          <div className="flex grow items-center pl-0.5">
            <div className="flex size-7 items-center justify-center">
              <div className="flex size-6 items-center justify-center rounded-lg dark:text-white">
                <Icon name={meta.icon ?? ""} className="size-4" />
              </div>
            </div>

            <div className="op-80 ml-1 text-xs leading-none font-medium tracking-wide uppercase dark:text-white">
              <span className="translate-y-px">{meta.title}</span>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-x-0.5 pr-0.5">
            <button
              type="button"
              className="flex size-7 items-center justify-center rounded-lg border border-transparent bg-transparent text-[var(--destructive)] transition outline-none hover:bg-[var(--background)] active:border-[var(--border)] active:bg-[var(--muted)]/50"
              onClick={() => deleteNode(id)}
            >
              <Icon name="mynaui:trash" className="size-4" />
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-col divide-y divide-[var(--border)]">
        <div className="relative flex min-h-10 flex-col">
          <div className="flex flex-col p-4">
            <div className="text-xs font-medium text-[var(--muted-foreground)]/50">
              Kategori vilkår
            </div>

            <div className="mt-2 flex">
              <ConditionDropdownSelector
                conditionsList={caseList}
                onChange={onConditionChange}
                value={data.condition}
              />
            </div>
            <CustomHandle
              type="target"
              id={targetHandleId}
              position={Position.Left}
              isConnectable={isConnectable}
              className="bottom-2! hover:!ring-2 hover:!ring-purple-500/50"
            />
          </div>
        </div>

        <div className="flex flex-col p-4">
          <div className="text-xs font-medium text-[var(--muted-foreground)]/50">
            Kategoriske situasjoner
          </div>

          {data.paths.length > 0 && (
            <div className="mt-2 flex flex-col">
              {data.paths.map((p) => (
                <NodePath
                  onRemove={removeNodePath}
                  key={p.id}
                  id={p.id}
                  isConnectable={true}
                  path={p} // ← no .case
                  /* … */
                />
              ))}
            </div>
          )}

          {filteredCaseList.length > 0 && (
            <div className="mt-2 flex">
              <DropdownMenu.Root>
                <DropdownMenu.Trigger asChild>
                  <button
                    type="button"
                    className="flex h-8 w-full items-center justify-center rounded-md border border-[var(--border)] bg-[var(--muted)] px-2.5 transition outline-none active:border-[var(--border)] active:bg-[var(--muted)]/50"
                    disabled={filteredCaseList.length === 0}
                  >
                    <div className="flex items-center text-xs font-medium">
                      <div className="text-xs leading-none font-medium tracking-wide dark:text-white">
                        Legg til en situasjon
                      </div>
                    </div>

                    <Icon
                      name="lucide:plus"
                      className="op-50 ml-1 size-4.5 dark:text-white"
                    />
                  </button>
                </DropdownMenu.Trigger>

                <DropdownMenu.Portal>
                  <DropdownMenu.Content
                    sideOffset={5}
                    align="start"
                    className={cn(
                      "w-fit rounded-lg border border-[var(--border)] bg-[var(--muted)]/90 p-0.5 text-[var(--foreground)] shadow-xl backdrop-blur-lg transition select-none",
                      "animate-in data-[side=top]:slide-in-bottom-0.5 data-[side=bottom]:slide-in-bottom--0.5 data-[side=bottom]:fade-in-40 data-[side=top]:fade-in-40",
                    )}
                  >
                    {filteredCaseList.map((c) => (
                      <DropdownMenu.Item
                        key={c.id}
                        className="flex h-8 w-full cursor-pointer items-center rounded-lg border border-transparent p-1.5 pr-6 transition outline-none hover:bg-[var(--background)] active:border-[var(--border)] active:bg-[var(--muted)]/50"
                        onSelect={() => addNodePath(c)}
                      >
                        <div className="flex items-center gap-x-2">
                          <div className="text-xs leading-none font-medium tracking-wide text-nowrap">
                            {c.value}
                          </div>
                        </div>
                      </DropdownMenu.Item>
                    ))}
                  </DropdownMenu.Content>
                </DropdownMenu.Portal>
              </DropdownMenu.Root>
            </div>
          )}
        </div>

        <div className="px-4 py-2">
          <div className="text-xs text-[var(--muted-foreground)]/50">
            This is a dummy conditional path node. Has no functionality for
            matching conditions.
          </div>
        </div>

        <div className="overflow-clip rounded-b-xl bg-[var(--muted)]/30 px-4 py-2 text-xs text-[var(--foreground)]/50">
          Node:{" "}
          <span className="font-semibold text-[var(--foreground)]/60">
            #{id}
          </span>
        </div>
      </div>
    </div>
  );
}
