import type { RegisterNodeMetadata } from "@/modules/nodes/types";
import { NODE_REGISTRY } from "./registry";
import "./loadfile";

export const NODES: RegisterNodeMetadata[] = Array.from(NODE_REGISTRY.values());

//todo: 1. Få mer zoom; 2. Over 1 til "end" input node.

export const NODE_TYPES = NODES.reduce(
  (acc, { type, node }) => {
    acc[type] = node;
    return acc;
  },
  {} as Record<string, any>,
);

export const AVAILABLE_NODES = NODES.filter(
  (node) => node.available === undefined || node.available,
).map((node) => ({
  type: node.type,
  icon: node.detail.icon,
  title: node.detail.title,
  description: node.detail.description,
}));
