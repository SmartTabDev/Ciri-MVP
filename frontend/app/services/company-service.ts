import axios from 'axios';

export interface CompanyData {
  id: number;
  name: string;
  business_email: string;
  business_category: string;
  terms_of_service: string;
  goal: string;
  phone_numbers?: string;
  follow_up_cycle?: number;
  gmail_box_email?: string;
  gmail_box_username?: string;
  gmail_box_credentials?: any;
  gmail_box_app_password?: string;
  outlook_box_email?: string;
  outlook_box_username?: string;
  outlook_box_credentials?: any;
  calendar_credentials?: any;
  instagram_credentials?: any;
  instagram_username?: string;
  instagram_account_id?: string;
  instagram_page_id?: string;
  facebook_box_credentials?: any;
  facebook_box_page_id?: string;
  facebook_box_page_name?: string;
  logo_url?: string;
  created_at: string;
  updated_at?: string;
}

export interface CompanyUpdateData {
  name?: string;
  business_email?: string;
  business_category?: string;
  terms_of_service?: string;
  goal?: string;
  phone_numbers?: string;
  follow_up_cycle?: number;
  gmail_box_email?: string;
  gmail_box_username?: string;
  gmail_box_credentials?: any;
  gmail_box_app_password?: string;
  outlook_box_email?: string;
  outlook_box_username?: string;
  outlook_box_credentials?: any;
  calendar_credentials?: any;
  instagram_credentials?: any;
  instagram_username?: string;
  instagram_account_id?: string;
  instagram_page_id?: string;
  facebook_box_credentials?: any;
  facebook_box_page_id?: string;
  facebook_box_page_name?: string;
}

export interface LogoUploadResponse {
  success: boolean;
  logo_url?: string;
  message?: string;
}

class CompanyService {
  private baseURL = `${process.env.NEXT_PUBLIC_API_URL}/v1` || 'https://cirinew.onrender.com/api/v1';

  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };
  }

  private getAuthHeadersForUpload() {
    const token = localStorage.getItem('access_token');
    return {
      'Authorization': `Bearer ${token}`,
    };
  }

  async getCompany(companyId: number): Promise<CompanyData> {
    try {
      console.log(`[CompanyService] Fetching company ${companyId} from: ${this.baseURL}/companies/${companyId}`);
      const response = await axios.get(`${this.baseURL}/companies/${companyId}`, {
        headers: this.getAuthHeaders(),
        withCredentials: true,
      });
      console.log(`[CompanyService] Successfully fetched company:`, response.data);
      return response.data;
    } catch (error: any) {
      console.error('[CompanyService] Error fetching company:', error);
      console.error('[CompanyService] Error response:', error.response?.data);
      console.error('[CompanyService] Error status:', error.response?.status);
      console.error('[CompanyService] Error headers:', error.response?.headers);
      throw error;
    }
  }

  async updateCompany(companyId: number, companyData: CompanyUpdateData): Promise<CompanyData> {
    try {
      const response = await axios.put(`${this.baseURL}/companies/${companyId}`, companyData, {
        headers: this.getAuthHeaders(),
        withCredentials: true,
      });
      return response.data;
    } catch (error) {
      console.error('Error updating company:', error);
      throw error;
    }
  }

  async uploadLogo(companyId: number, file: File): Promise<LogoUploadResponse> {
    try {
      const formData = new FormData();
      formData.append('logo', file);

      const response = await axios.post(
        `${this.baseURL}/companies/${companyId}/logo`,
        formData,
        {
          headers: {
            ...this.getAuthHeadersForUpload(),
            'Content-Type': 'multipart/form-data',
          },
          withCredentials: true,
        }
      );

      return response.data;
    } catch (error: any) {
      console.error('Error uploading logo:', error);
      throw new Error(error.response?.data?.detail || 'Failed to upload logo');
    }
  }

  async getLogo(companyId: number): Promise<string | null> {
    try {
      const response = await axios.get(
        `${this.baseURL}/companies/${companyId}/logo`,
        {
          headers: this.getAuthHeadersForUpload(),
          withCredentials: true,
        }
      );

      return response.data.logo_url || null;
    } catch (error) {
      console.error('Error fetching logo:', error);
      return null;
    }
  }
}

export const companyService = new CompanyService(); 