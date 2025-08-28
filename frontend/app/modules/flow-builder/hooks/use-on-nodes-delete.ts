"use client";
import { useCallback } from "react";

import type { Node } from "@xyflow/react";

import { useMotherStore } from "@/stores/motherStore";

export function useOnNodesDelete(nodes: Node[]) {
  const { nodePropertiesSelectedNode, nodePropertiesSetSelectedNode } =
    useMotherStore((s) => ({
      nodePropertiesSelectedNode: s.sidebar.panels.nodeProperties.selectedNode,
      nodePropertiesSetSelectedNode:
        s.actions.sidebar.panels.nodeProperties.setSelectedNode,
    }));

  return useCallback(
    (_: Node[]) => {
      if (
        nodePropertiesSelectedNode &&
        !nodes.find((node) => node.id === nodePropertiesSelectedNode.id)
      )
        nodePropertiesSetSelectedNode(null);
    },
    [nodePropertiesSelectedNode, nodePropertiesSetSelectedNode, nodes],
  );
}
