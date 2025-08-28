import { useInsertNode } from "@/modules/flow-builder/hooks/use-insert-node";
import { AVAILABLE_NODES } from "@/modules/nodes";
import SidebarPanelWrapper from "@/modules/sidebar/components/sidebar-panel-wrapper";
import { NodePreviewDraggable } from "@/modules/sidebar/panels/available-nodes/components/node-preview-draggable";
import { useMotherStore } from "@/stores/motherStore";
import Icon from "@/components/icon-component";

export default function AvailableNodesPanel() {
  const { isMobileView, setActivePanel } = useMotherStore((s) => ({
    isMobileView: s.view.mobile,
    setActivePanel: s.actions.sidebar.setActivePanel,
  }));
  const insertNode = useInsertNode();

  return (
    <SidebarPanelWrapper>
      <div className="mt-4 flex flex-col items-center p-4 text-center">
        <div className="flex size-12 items-center justify-center rounded-full bg-[var(--primary)]">
          <Icon
            name="mynaui:grid"
            className="size-6 text-[var(--primary-foreground)]"
          />
        </div>

        <div className="mt-4 font-medium text-[var(--text-main)]!">
          Treningsmoduler
        </div>

        <div className="mt-1 w-2/3 text-xs leading-normal font-medium text-[var(--muted-foreground)]/40">
          {isMobileView
            ? "Tap on a node to add it to your chatbot flow"
            : "Dra boksene enkelt inn for å spesifisere treningsprogrammet"}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 p-4">
        {AVAILABLE_NODES.map((node) => (
          <NodePreviewDraggable
            key={node.type}
            type={node.type}
            icon={node.icon}
            title={node.title}
            description={node.description}
            isMobileView={isMobileView}
            setActivePanel={setActivePanel}
            insertNode={insertNode}
          />
        ))}
      </div>
    </SidebarPanelWrapper>
  );
}
