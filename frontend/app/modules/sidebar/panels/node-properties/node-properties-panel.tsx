import { useNodes, useReactFlow } from "@xyflow/react";
import { produce } from "immer";
import { OverlayScrollbarsComponent } from "overlayscrollbars-react";
import { useMemo } from "react";
import SplitPane, { Pane } from "split-pane-react";

import { BuilderNode } from "@/modules/nodes/types";
import SidebarPanelHeading from "@/modules/sidebar/components/sidebar-panel-heading";
import SidebarPanelWrapper from "@/modules/sidebar/components/sidebar-panel-wrapper";
import { NodeListItem } from "@/modules/sidebar/panels/node-properties/components/node-list-item";
import { NodePropertyPanel } from "@/modules/sidebar/panels/node-properties/components/node-propery-panel";
import { useNodeList } from "@/modules/sidebar/panels/node-properties/hooks/use-node-list";
import IntroductionPropertyPanel from "@/modules/sidebar/panels/node-properties/property-panels/introduction-property-panel";
import { useMotherStore } from "@/stores/motherStore";

import { defaultOverlayScrollbarsOptions } from "@/lib/overlayscrollbars";
import Icon from "@/components/icon-component";

export function NodePropertiesPanel() {
  const { paneSizes, selectedNode, setPaneSizes, setSelectedNode } =
    useMotherStore((s) => ({
      paneSizes: s.sidebar.panels.nodeProperties.paneSizes,
      setPaneSizes: s.actions.sidebar.panels.nodeProperties.setPaneSizes,
      selectedNode: s.sidebar.panels.nodeProperties.selectedNode,
      setSelectedNode: s.actions.sidebar.panels.nodeProperties.setSelectedNode,
    }));

  const nodes = useNodes();

  const nodeList = useNodeList(nodes);

  const { setNodes } = useReactFlow();

  const onNodeClick = (id: string) => {
    setNodes((nds) =>
      produce(nds, (draft) => {
        draft.forEach((node) => {
          node.selected = node.id === id;
        });
      }),
    );

    setSelectedNode({
      id,
      type: nodeList.find((n) => n.id === id)?.type as BuilderNode,
    });
  };

  const selectedNodeData = useMemo(() => {
    return nodes.find((n) => n.id === selectedNode?.id)?.data;
  }, [nodes, selectedNode?.id]);

  return (
    <SidebarPanelWrapper>
      <SplitPane
        sizes={paneSizes}
        sashRender={() => (
          <div className="m h-0.5 bg-[var(--border)] transition md:hover:scale-y-200 md:hover:bg-[var(--border)]" />
        )}
        onChange={setPaneSizes}
        split="horizontal"
      >
        <Pane minSize={200}>
          <div className="flex h-full flex-col">
            <SidebarPanelHeading className="shrink-0">
              <Icon name="mynaui:layers-three" className="size-4.5" />
              Nodes in Flow
            </SidebarPanelHeading>

            <OverlayScrollbarsComponent
              className="grow"
              defer
              options={defaultOverlayScrollbarsOptions}
            >
              <div className="flex flex-col gap-1 p-1.5">
                {nodeList.map((node) => (
                  <NodeListItem
                    key={node.id}
                    id={
                      node.type === BuilderNode.START ||
                      node.type === BuilderNode.END
                        ? undefined
                        : node.id
                    }
                    title={node.detail.title}
                    icon={`${node.detail.icon} ${node.type === BuilderNode.START || node.type === BuilderNode.END ? "scale-135" : ""}`}
                    selected={selectedNode?.id === node.id}
                    pseudoSelected={node.selected}
                    onClick={() => {
                      onNodeClick(node.id);
                    }}
                  />
                ))}
              </div>
            </OverlayScrollbarsComponent>
          </div>
        </Pane>

        <Pane minSize={300}>
          <div className="flex h-full flex-col">
            <SidebarPanelHeading className="shrink-0">
              <Icon name="mynaui:cog" className="size-4.5" />
              Properties
            </SidebarPanelHeading>

            <OverlayScrollbarsComponent
              className="grow"
              defer
              options={defaultOverlayScrollbarsOptions}
            >
              {selectedNode ? (
                <NodePropertyPanel
                  id={selectedNode.id}
                  type={selectedNode.type}
                  data={selectedNodeData}
                />
              ) : (
                <IntroductionPropertyPanel />
              )}
            </OverlayScrollbarsComponent>
          </div>
        </Pane>
      </SplitPane>
    </SidebarPanelWrapper>
  );
}
