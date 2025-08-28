import type { BuilderNodeType, RegisterNodeMetadata } from "./types";

export const NODE_REGISTRY = new Map<BuilderNodeType, RegisterNodeMetadata>();

console.log("Node registry data: ", NODE_REGISTRY);
