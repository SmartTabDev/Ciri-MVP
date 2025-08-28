import { create } from 'zustand';
import { flowContextService, FlowData, CompanyContext } from '@/services/flow-context-service';

interface FlowState {
  nodes: any[];
  edges: any[];
  companyContext: CompanyContext | null;
  companyId: number | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  flowContextText: string | null;
  
  // Actions
  setNodes: (nodes: any[]) => void;
  setEdges: (edges: any[]) => void;
  setCompanyId: (companyId: number) => void;
  setError: (error: string | null) => void;
  setFlowContextText: (text: string | null) => void;
  
  // Async actions
  loadFlowContext: (companyId: number) => Promise<{ nodes: any[]; edges: any[] } | null>;
  saveFlowContext: (companyId: number) => Promise<void>;
  updateFlowBuilderData: (companyId: number) => Promise<void>;
  loadFlowContextText: (companyId: number) => Promise<void>;
  resetFlow: () => void;
}

export const useFlowStore = create<FlowState>((set, get) => ({
  nodes: [],
  edges: [],
  companyContext: null,
  companyId: null,
  isLoading: false,
  isSaving: false,
  error: null,
  flowContextText: null,

  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  setCompanyId: (companyId) => set({ companyId }),
  setError: (error) => set({ error }),
  setFlowContextText: (text) => set({ flowContextText: text }),

  loadFlowContext: async (companyId: number) => {
    set({ isLoading: true, error: null });
    try {
      const flowData = await flowContextService.getFlowContext(companyId);
      if (flowData) {
        const nodes = flowData.nodes || [];
        const edges = flowData.edges || [];
        set({ nodes, edges, companyId });
        return { nodes, edges };
      } else {
        set({ nodes: [], edges: [], companyId });
        return null;
      }
    } catch (error: any) {
      set({ error: error.message || 'Failed to load flow context', nodes: [], edges: [], companyId });
      throw error;
    } finally {
      set({ isLoading: false });
    }
  },

  saveFlowContext: async (companyId: number) => {
    const { nodes, edges } = get();
    set({ isSaving: true, error: null });
    try {
      const flowData: FlowData = { nodes, edges };
      const companyContext = await flowContextService.saveFlowContext(companyId, flowData);
      set({ companyContext });
    } catch (error: any) {
      set({ error: error.message || 'Failed to save flow context' });
      throw error;
    } finally {
      set({ isSaving: false });
    }
  },

  updateFlowBuilderData: async (companyId: number) => {
    const { nodes, edges } = get();
    set({ isSaving: true, error: null });
    try {
      const flowData: FlowData = { nodes, edges };
      const companyContext = await flowContextService.updateFlowBuilderData(companyId, flowData);
      set({ companyContext });
      
      // Also load the generated flow context text
      await get().loadFlowContextText(companyId);
    } catch (error: any) {
      set({ error: error.message || 'Failed to update flow builder data' });
      throw error;
    } finally {
      set({ isSaving: false });
    }
  },

  loadFlowContextText: async (companyId: number) => {
    try {
      const flowContextText = await flowContextService.getFlowContextText(companyId);
      set({ flowContextText });
    } catch (error: any) {
      console.error('Error loading flow context text:', error);
      set({ flowContextText: null });
    }
  },

  resetFlow: () => {
    set({
      nodes: [],
      edges: [],
      companyContext: null,
      error: null,
      flowContextText: null,
    });
  },
})); 