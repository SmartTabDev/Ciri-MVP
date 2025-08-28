"use client";
import {
  Controls,
  type ReactFlowState,
  useReactFlow,
  useStore,
} from "@xyflow/react";
import { shallow } from "zustand/shallow";

import CustomControlButton from "@/modules/flow-builder/components/controls/custom-control-button";
import { useMotherStore } from "@/stores/motherStore";
import Icon from "@/components/icon-component";

const ZOOM_DURATION = 500;

function selector(s: ReactFlowState) {
  return {
    minZoomReached: s.transform[2] <= s.minZoom,
    maxZoomReached: s.transform[2] >= s.maxZoom,
  };
}

export default function CustomControls() {
  const [isMobile] = useMotherStore((s) => [s.view.mobile]);

  const { maxZoomReached, minZoomReached } = useStore(selector, shallow);
  const { zoomIn, zoomOut, fitView } = useReactFlow();

  return (
    <Controls
      showFitView={false}
      showZoom={false}
      className="!bg-[var(--primary-foreground)]"
      showInteractive={false}
      position={!isMobile ? "bottom-left" : "top-right"}
    >
      <CustomControlButton
        onClick={() => zoomIn({ duration: ZOOM_DURATION })}
        disabled={maxZoomReached}
      >
        <Icon name="mynaui:plus" className="size-5" />
      </CustomControlButton>

      <CustomControlButton
        onClick={() => zoomOut({ duration: ZOOM_DURATION })}
        disabled={minZoomReached}
      >
        <Icon name="mynaui:minus" className="size-5" />
      </CustomControlButton>

      <CustomControlButton onClick={() => fitView({ duration: ZOOM_DURATION })}>
        <Icon name="mynaui:maximize" className="size-4" />
      </CustomControlButton>
    </Controls>
  );
}
