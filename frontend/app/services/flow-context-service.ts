import axios from 'axios';

export interface FlowData {
  nodes: any[];
  edges: any[];
}

export interface CompanyContext {
  id: number;
  company_id: number;
  text_context?: string;
  flow_builder_data?: string;
  flow_context?: string;
  created_at: string;
  updated_at?: string;
}

class FlowContextService {
  private baseURL = `${process.env.NEXT_PUBLIC_API_URL}/v1` || 'https://cirinew.onrender.com/api/v1';

  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Refresh-Token': refreshToken || '',
    };
  }

  async getFlowContext(companyId: number): Promise<FlowData | null> {
    try {
      console.log(`[FlowContextService] Fetching flow context for company ${companyId} from: ${this.baseURL}/company-context/company/${companyId}`);
      const response = await axios.get<CompanyContext>(
        `${this.baseURL}/company-context/company/${companyId}`,
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );
      console.log(`[FlowContextService] Successfully fetched flow context:`, response.data);

      if (response.data.flow_builder_data) {
        return JSON.parse(response.data.flow_builder_data);
      }
      return null;
    } catch (error: any) {
      console.error('[FlowContextService] Error fetching flow context:', error);
      console.error('[FlowContextService] Error response:', error.response?.data);
      console.error('[FlowContextService] Error status:', error.response?.status);
      console.error('[FlowContextService] Error headers:', error.response?.headers);
      return null;
    }
  }

  async saveFlowContext(companyId: number, flowData: FlowData): Promise<CompanyContext> {
    try {
      console.log(`[FlowContextService] Saving flow context for company ${companyId} to: ${this.baseURL}/company-context/company/${companyId}/flow-builder-data`);
      console.log(`[FlowContextService] Flow data:`, flowData);
      
      const response = await axios.put<CompanyContext>(
        `${this.baseURL}/company-context/company/${companyId}/flow-builder-data`,
        flowData,
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );
      console.log(`[FlowContextService] Successfully saved flow context:`, response.data);
      return response.data;
    } catch (error: any) {
      console.error('[FlowContextService] Error saving flow context:', error);
      console.error('[FlowContextService] Error response:', error.response?.data);
      console.error('[FlowContextService] Error status:', error.response?.status);
      console.error('[FlowContextService] Error headers:', error.response?.headers);
      throw error;
    }
  }

  async updateFlowBuilderData(companyId: number, flowData: FlowData): Promise<CompanyContext> {
    try {
      const response = await axios.put<CompanyContext>(
        `${this.baseURL}/company-context/company/${companyId}/flow-builder-data`,
        flowData,
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );
      return response.data;
    } catch (error) {
      console.error('Error updating flow builder data:', error);
      throw error;
    }
  }

  async getFlowContextText(companyId: number): Promise<string | null> {
    try {
      const response = await axios.get<CompanyContext>(
        `${this.baseURL}/company-context/company/${companyId}`,
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );

      return response.data.flow_context || null;
    } catch (error) {
      console.error('Error fetching flow context text:', error);
      return null;
    }
  }
}

export const flowContextService = new FlowContextService(); 