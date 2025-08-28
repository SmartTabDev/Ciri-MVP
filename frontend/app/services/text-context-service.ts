import axios from 'axios';

export interface TextContextData {
  text_context: string;
}

class TextContextService {
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

  async getTextContext(companyId: number): Promise<string | null> {
    try {
      console.log(`[TextContextService] Fetching text context for company ${companyId} from: ${this.baseURL}/company-context/company/${companyId}`);
      const response = await axios.get(
        `${this.baseURL}/company-context/company/${companyId}`,
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );
      console.log(`[TextContextService] Successfully fetched text context:`, response.data);
      return response.data.text_context || null;
    } catch (error: any) {
      console.error('[TextContextService] Error fetching text context:', error);
      console.error('[TextContextService] Error response:', error.response?.data);
      console.error('[TextContextService] Error status:', error.response?.status);
      console.error('[TextContextService] Error headers:', error.response?.headers);
      return null;
    }
  }

  async saveTextContext(companyId: number, textContext: string): Promise<boolean> {
    try {
      const response = await axios.put(
        `${this.baseURL}/company-context/company/${companyId}/text-context`,
        {
          text_context: textContext,
        },
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );

      return true;
    } catch (error) {
      console.error('Error saving text context:', error);
      throw error;
    }
  }

  async createTextContext(companyId: number, textContext: string): Promise<boolean> {
    try {
      const response = await axios.post(
        `${this.baseURL}/company-context/`,
        {
          company_id: companyId,
          text_context: textContext,
        },
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );

      return true;
    } catch (error) {
      console.error('Error creating text context:', error);
      throw error;
    }
  }
}

export const textContextService = new TextContextService(); 