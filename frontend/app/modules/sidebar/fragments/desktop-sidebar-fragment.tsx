"use client";
import { useEffect } from "react";

import type { ApplicationState } from "@/stores/application-state";

import SidebarButtonItem from "@/modules/sidebar/components/sidebar-button-item";
import { SwitchSidebarPanel } from "@/modules/sidebar/components/sidebar-switch-panel";
import Icon from "@/components/icon-component";

type DesktopSidebarFragmentProps = Readonly<{
  isMobileView: ApplicationState["view"]["mobile"];
  activePanel: ApplicationState["sidebar"]["active"];
  setActivePanel: (panel: ApplicationState["sidebar"]["active"]) => void;
}>;

export function DesktopSidebarFragment({
  isMobileView,
  activePanel,
  setActivePanel,
}: DesktopSidebarFragmentProps) {
  useEffect(() => {
    if (!isMobileView && activePanel === "none") {
      setActivePanel("available-nodes");
    }
  }, [activePanel, setActivePanel, isMobileView]);

  return (
    <div className="relative flex h-screen w-fit max-w-sm shrink-0 divide-x border-neutral-600 text-[var(--primary)]">
      {activePanel !== "none" && (
        <div className="min-w-xs grow bg-[var(--background)]">
          <SwitchSidebarPanel active={activePanel} />
        </div>
      )}

      <div className="shrink-0 bg-[var(--muted)] p-1.5">
        <div className="flex h-full flex-col gap-2">
          <SidebarButtonItem
            active={activePanel === "available-nodes"}
            onClick={() => setActivePanel("available-nodes")}
          >
            <Icon name="mynaui:grid" className="size-5" />
          </SidebarButtonItem>

          <div className="mx-auto h-px w-4 bg-[var(--border)]" />

          <SidebarButtonItem
            active={activePanel === "node-properties"}
            onClick={() => setActivePanel("node-properties")}
          >
            <Icon name="mynaui:layers-three" className="size-5" />
          </SidebarButtonItem>
        </div>
      </div>
    </div>
  );
}
