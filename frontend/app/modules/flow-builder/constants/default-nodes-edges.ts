"use client";
import { nanoid } from "nanoid";
import { caseList } from "@/modules/nodes/nodes/conditional-path-node/conditional-path.node";
import { BuilderNode } from "@/modules/nodes/types";
import { createNodeWithDefaultData } from "@/modules/nodes/utils";

//This is the first rendered nodes when the user lands on the page for the first time.
const returnWarrantyFirstRender = caseList.find(
  (c) => c.type === "return_warranty",
);

const [pathValueA, pathValueB] = returnWarrantyFirstRender?.paths.values ?? [];

const pathA = { id: nanoid(), value: pathValueA };
const pathB = { id: nanoid(), value: pathValueB };

const startNode = createNodeWithDefaultData(BuilderNode.START, {
  position: { x: 0, y: 100 },
});

const conditionalNode = createNodeWithDefaultData(
  BuilderNode.CONDITIONAL_PATH,
  {
    position: { x: 250, y: 50 },
    data: {
      condition: {
        id: returnWarrantyFirstRender?.id,
        label: returnWarrantyFirstRender?.label,
      },
      paths: [pathA, pathB],
    },
  },
);

const textMsgNodeA = createNodeWithDefaultData(BuilderNode.TEXT_MESSAGE, {
  position: { x: 800, y: -50 },
  data: {
    channel: "sms",
    message: "Om kunden ønsker å returnere en vare, gjør dette . . . ",
  },
});
const textMsgNodeB = createNodeWithDefaultData(BuilderNode.TEXT_MESSAGE, {
  position: { x: 800, y: 250 },
  data: {
    channel: "sms",
    message:
      "Om kunden stiller spørsmål rundt retur og garanti, gjør dette . . . ",
  },
});

const endNode = createNodeWithDefaultData(BuilderNode.END, {
  position: { x: 1300, y: 100 },
});

const nodes = [startNode, endNode];

export const edges = [
  {
    id: nanoid(),
    source: startNode.id,
    target: conditionalNode.id,
    type: "deletable",
  },
  {
    id: nanoid(),
    source: conditionalNode.id,
    sourceHandle: pathA.id, // ⬅ important: match the handle
    target: textMsgNodeA.id,
    type: "deletable",
  },
  {
    id: nanoid(),
    source: conditionalNode.id,
    sourceHandle: pathB.id, // ⬅ important: match the handle
    target: textMsgNodeB.id,
    type: "deletable",
  },
  {
    id: nanoid(),
    source: textMsgNodeA.id,
    target: endNode.id,
    type: "deletable",
  },
  {
    id: nanoid(),
    source: textMsgNodeB.id,
    target: endNode.id,
    type: "deletable",
  },
];

export { nodes as defaultNodes, edges as defaultEdges };
