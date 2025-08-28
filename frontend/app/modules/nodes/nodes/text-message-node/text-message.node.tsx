"use client";
import {
  type Node,
  type NodeProps,
  Position,
  useReactFlow,
} from "@xyflow/react";
import { produce } from "immer";
import { nanoid } from "nanoid";
import { isEmpty } from "radash";
import { memo, useCallback, useMemo, useState, useEffect } from "react";

import CustomHandle from "@/modules/flow-builder/components/handles/custom-handle";
import { useDeleteNode } from "@/modules/flow-builder/hooks/use-delete-node";
import { MessageChannelSelector } from "@/modules/nodes/nodes/text-message-node/components/message-channel-selector";
import {
  type MessageChannelDetail,
  type MessageChannelType,
  getMessageChannelDetails,
} from "@/modules/nodes/nodes/text-message-node/constants/channels";
import {
  type BaseNodeData,
  BuilderNode,
  type RegisterNodeMetadata,
} from "@/modules/nodes/types";

import TextMessageNodePropertyPanel from "@/modules/sidebar/panels/node-properties/property-panels/text-message-property-panel";
import { useMotherStore } from "@/stores/motherStore";
import { NODE_REGISTRY } from "../../registry";

import { cn } from "@/lib/utils";
import Icon from "@/components/icon-component";

const NODE_TYPE = BuilderNode.TEXT_MESSAGE;

export interface TextMessageNodeData extends BaseNodeData {
  channel: MessageChannelType;
  message: string;
  sourceHandleId?: string; // Add stable handle ID for source
  targetHandleId?: string; // Add stable handle ID for target
}

type TextMessageNodeProps = NodeProps<
  Node<TextMessageNodeData, typeof NODE_TYPE>
>;

// eslint-disable-next-line react-refresh/only-export-components
export const metadata: RegisterNodeMetadata<TextMessageNodeData> = {
  type: NODE_TYPE,
  node: memo(TextMessageNode),
  detail: {
    icon: "mynaui:chat",
    title: "Instruks",
    description:
      "Send a text message to the user using different messaging platforms like WhatsApp, Messenger, etc.",
  },
  defaultData: {
    channel: "sms",
    message: "",
  },
  propertyPanel: TextMessageNodePropertyPanel,
};

NODE_REGISTRY.set(metadata.type, metadata);

export function TextMessageNode({
  id,
  isConnectable,
  selected,
  data,
}: TextMessageNodeProps) {
  const meta = metadata.detail;

  const [showNodePropertiesOf] = useMotherStore((s) => [
    s.actions.sidebar.showNodePropertiesOf,
  ]);
  
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

  const { setNodes } = useReactFlow();
  const deleteNode = useDeleteNode();

  const messageChannelDetail = useMemo(() => {
    return getMessageChannelDetails(data.channel);
  }, [data.channel]);

  const onMessageChannelSelect = useCallback(
    (channel: MessageChannelDetail & { type: MessageChannelType }) => {
      setNodes((nodes) =>
        produce(nodes, (draft) => {
          const node = draft.find((node) => node.id === id);

          if (node) node.data.channel = channel.type;
        }),
      );
    },
    [id, setNodes],
  );

  const showNodeProperties = useCallback(() => {
    showNodePropertiesOf({ id, type: NODE_TYPE });
  }, [id, showNodePropertiesOf]);

  return (
    <>
      <div
        data-selected={selected}
        className="w-xs divide-y divide-[var(--border)] overflow-clip rounded-xl border border-[var(--border)] bg-[var(--muted)]/50 text-[var(--primary)] shadow-sm ring-1 backdrop-blur-xl transition data-[selected=true]:border-emerald-500 data-[selected=true]:ring-emerald-500/50"
        onDoubleClick={showNodeProperties}
      >
        <div className="relative bg-[var(--muted)]/50">
          <div className="absolute inset-0">
            <div className="absolute h-full w-3/5 bg-gradient-to-r from-emerald-500/20 to-transparent" />
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
              <MessageChannelSelector
                detail={messageChannelDetail}
                onSelect={onMessageChannelSelect}
              />

              <div className="mx-1 h-4 w-px bg-[var(--border)]" />

              <button
                type="button"
                className="flex size-7 items-center justify-center rounded-lg border border-transparent bg-transparent transition outline-none hover:bg-[var(--background)] active:border-[var(--border)] active:bg-[var(--muted)]/50"
                onClick={() => showNodeProperties()}
              >
                <Icon name="mynaui:cog" className="size-4" />
              </button>

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
          <div className="flex flex-col p-4">
            <div className="text-xs font-medium text-[var(--muted-foreground)]/50">
              Instruks innhold
            </div>

            <div className="mt-2 line-clamp-4 text-sm leading-snug dark:text-white">
              {isEmpty(data.message) ? (
                <span className="text-[var(--muted-foreground)]/80 italic">
                  Ingen instrukser enda. Dobbel-trykk på denne boksen og skriv
                  inn instruks i sidemenyen til høyre.
                </span>
              ) : (
                data.message
              )}
            </div>
          </div>

          <div className="px-4 py-2">
            <div className="text-xs text-[var(--muted-foreground)]/50">
              Dobbeltrykk på boksen og rediger teksten i høyre sidemeny.{" "}
              {/* <b className="font-semibold text-[var(--muted-foreground)]/60">
                "{messageChannelDetail.name}"
              </b>{" "}
              channel. */}
            </div>
          </div>

          {/* <div className="bg-[var(--muted)]/30 px-4 py-2 text-xs text-[var(--muted-foreground)]/50">
            Treningsnode nr:{" "}
            <span className="font-semibold text-[var(--muted-foreground)]/60">
              #{id}
            </span>
          </div> */}
        </div>
      </div>

      <CustomHandle
        type="target"
        id={targetHandleId}
        position={Position.Left}
        isConnectable={isConnectable}
      />

      <CustomHandle
        type="source"
        id={sourceHandleId}
        position={Position.Right}
        isConnectable={isConnectable}
      />
    </>
  );
}
