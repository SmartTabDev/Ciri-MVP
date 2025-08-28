import { StateCreator } from "zustand";
import { BuilderNodeType } from "@/modules/nodes/types";

export interface ApplicationSlice {
  view: {
    mobile: boolean;
  };
  sidebar: {
    active: "node-properties" | "available-nodes" | "none";
    panels: {
      nodeProperties: {
        selectedNode: { id: string; type: BuilderNodeType } | null | undefined;
        paneSizes: (string | number)[];
      };
    };
  };
  actions: {
    view: {
      setMobileView: (isMobile: boolean) => void;
    };
    sidebar: {
      setActivePanel: (
        panel: "node-properties" | "available-nodes" | "none",
      ) => void;
      showNodePropertiesOf: (node: {
        id: string;
        type: BuilderNodeType;
      }) => void;
      panels: {
        nodeProperties: {
          setSelectedNode: (
            node: { id: string; type: BuilderNodeType } | undefined | null,
          ) => void;
          setPaneSizes: (sizes: (string | number)[]) => void;
        };
      };
    };
  };
}

export const createApplicationSlice: StateCreator<
  ApplicationSlice,
  [["zustand/immer", never]],
  [],
  ApplicationSlice
> = (set) => ({
  view: {
    mobile: false,
  },
  sidebar: {
    active: "none",
    panels: {
      nodeProperties: {
        selectedNode: null,
        paneSizes: ["40%", "auto"],
      },
    },
  },
  actions: {
    view: {
      setMobileView(isMobile) {
        set((state) => {
          state.view.mobile = isMobile;
        });
      },
    },
    sidebar: {
      setActivePanel(panel) {
        set((state) => {
          state.sidebar.active = panel;
        });
      },
      showNodePropertiesOf(node) {
        set((state) => {
          state.sidebar.active = "node-properties";
          state.sidebar.panels.nodeProperties.selectedNode = node;
        });
      },
      panels: {
        nodeProperties: {
          setSelectedNode(node) {
            set((state) => {
              state.sidebar.panels.nodeProperties.selectedNode = node;
            });
          },
          setPaneSizes(sizes) {
            set((state) => {
              state.sidebar.panels.nodeProperties.paneSizes = sizes;
            });
          },
        },
      },
    },
  },
});
