"use client";
import { FlowBuilderModule } from "@/modules/flow-builder/flow-builder-module";
import { SidebarModule } from "@/modules/sidebar/sidebar-module";

import { ReactFlowProvider } from "@xyflow/react";
import React, { Fragment } from "react";
import "@xyflow/react/dist/style.css";
import "overlayscrollbars/styles/overlayscrollbars.css";
import "split-pane-react/esm/themes/default.css";
import { NavigationBarModule } from "@/modules/navigation-bar/navigation-bar-module";

function page() {
  return (
    <Fragment>
      <ReactFlowProvider>
        <div>
          <NavigationBarModule />
        </div>
        <div
          className="training-page flex h-full grow divide-x overflow-y-hidden border-neutral-600"
          style={{ height: "calc(100vh - 96px)" }}
        >
          <div className="grow bg-[var(--muted)]">
            <FlowBuilderModule />
          </div>
          <div className="bg-neutral-800">
            <SidebarModule />
          </div>
        </div>
      </ReactFlowProvider>
    </Fragment>
  );
}

export default page;
