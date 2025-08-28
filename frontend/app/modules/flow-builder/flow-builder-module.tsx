"use client";
import {
  Background,
  type Connection,
  type Edge,
  type EdgeTypes,
  type Node,
  type NodeChange,
  ReactFlow,
  addEdge,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from "@xyflow/react";
import { nanoid } from "nanoid";
import { useCallback, useEffect } from "react";

import CustomControls from "@/modules/flow-builder/components/controls/custom-controls";
import CustomDeletableEdge from "@/modules/flow-builder/components/edges/custom-deletable-edge";
import {
  defaultEdges,
  defaultNodes,
} from "@/modules/flow-builder/constants/default-nodes-edges";
import { useDeleteKeyCode } from "@/modules/flow-builder/hooks/use-delete-key-code";
import { useDragDropFlowBuilder } from "@/modules/flow-builder/hooks/use-drag-drop-flow-builder";
import { useIsValidConnection } from "@/modules/flow-builder/hooks/use-is-valid-connection";
import { useNodeAutoAdjust } from "@/modules/flow-builder/hooks/use-node-auto-adjust";
import { useOnNodesDelete } from "@/modules/flow-builder/hooks/use-on-nodes-delete";
import { NODE_TYPES } from "@/modules/nodes";
import { setAutoFreeze } from "immer";
import { useMotherStore } from "@/stores/motherStore";
import { useFlowStore } from "@/stores/flowStore";
import { useUser } from "@/contexts/user-context";

const edgeTypes: EdgeTypes = {
  deletable: CustomDeletableEdge,
};

setAutoFreeze(false);

export function FlowBuilderModule() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const { getNodes } = useReactFlow();
  const deleteKeyCode = useDeleteKeyCode();
  const onNodesDelete = useOnNodesDelete(nodes);
console.log(nodes, edges)
  const autoAdjustNode = useNodeAutoAdjust();

  const [onDragOver, onDrop] = useDragDropFlowBuilder();
  const isValidConnection = useIsValidConnection(nodes, edges);

  // Get company ID from user context
  const { user, loading: userLoading } = useUser();
  const companyId = user?.company_id;

  // Flow store integration
  const {
    loadFlowContext,
    saveFlowContext,
    isLoading: isLoadingFlow,
    isSaving,
    error,
  } = useFlowStore();

  // Load flow context when company ID is available
  useEffect(() => {
    if (companyId && !userLoading) {
      loadFlowContext(companyId).then((flowData) => {
        if (flowData) {
          // Set nodes and edges from backend response
          setNodes(flowData.nodes);
          setEdges(flowData.edges);
        } else {
          setNodes(defaultNodes);
        }
      }).catch((error) => {
        console.error('Error loading flow context:', error);
      });
    }
  }, [companyId, userLoading, loadFlowContext, setNodes, setEdges]);

  // Sync flow store with React Flow state (only for user changes)
  useEffect(() => {
    const { setNodes: setStoreNodes, setEdges: setStoreEdges } = useFlowStore.getState();
    setStoreNodes(nodes);
    setStoreEdges(edges);
  }, [nodes, edges]);

  const onConnect = useCallback(
    (connection: Connection) => {
      const edge = { ...connection, id: nanoid(), type: "deletable" } as Edge;
      setEdges((edges) => addEdge(edge, edges));
    },
    [setEdges],
  );

  const handleAutoAdjustNodeAfterNodeMeasured = useCallback(
    (id: string) => {
      setTimeout(() => {
        const node = getNodes().find((n) => n.id === id);
        if (!node) {
          return;
        }

        if (node.measured === undefined) {
          handleAutoAdjustNodeAfterNodeMeasured(id);
          return;
        }

        autoAdjustNode(node);
      });
    },
    [autoAdjustNode, getNodes],
  );

  const handleNodesChange = useCallback(
    (changes: NodeChange[]) => {
      onNodesChange(changes);

      changes.forEach((change) => {
        if (change.type === "dimensions") {
          const node = getNodes().find((n) => n.id === change.id);
          if (node) {
            autoAdjustNode(node);
          }
        }

        if (change.type === "add") {
          handleAutoAdjustNodeAfterNodeMeasured(change.item.id);
        }
      });
    },
    [
      autoAdjustNode,
      getNodes,
      handleAutoAdjustNodeAfterNodeMeasured,
      onNodesChange,
    ],
  );

  // Show loading state
  if (userLoading || isLoadingFlow) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
          <p className="text-sm text-muted-foreground">
            {userLoading ? "Loading user info..." : "Loading flow..."}
          </p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-sm text-destructive mb-2">Error loading flow</p>
          <p className="text-xs text-muted-foreground">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <ReactFlow
      proOptions={{ hideAttribution: true }}
      nodeTypes={NODE_TYPES}
      onInit={({ fitView }) => fitView().then()}
      nodes={nodes}
      onNodesChange={handleNodesChange}
      edgeTypes={edgeTypes}
      edges={edges}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onNodeDragStop={(_, node) => {
        autoAdjustNode(node);
      }}
      onNodesDelete={onNodesDelete}
      isValidConnection={isValidConnection}
      multiSelectionKeyCode={null}
      deleteKeyCode={deleteKeyCode}
      snapGrid={[16, 16]}
      snapToGrid
      fitView
    >
      <Background color={"var(--background)"} gap={32} />
      <CustomControls />
    </ReactFlow>
  );
}
