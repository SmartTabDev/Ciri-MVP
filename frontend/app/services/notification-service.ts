import axios from 'axios';

export interface NotificationUpdateRequest {
  notification_read: boolean;
}

export interface BulkNotificationUpdateRequest {
  message_ids: string[];
  notification_read: boolean;
}

export interface NotificationResponse {
  success: boolean;
  message: string;
  notification_read: boolean;
}

export interface UnreadNotificationCount {
  unread_count: number;
  company_id: number;
}

export interface UnreadNotification {
  message_id: string;
  channel_id: string;
  from_email: string;
  subject: string;
  sent_at: string;
  action_required: boolean;
  action_reason: string;
  action_type: string;
  urgency: string;
  notification_read: boolean;
}

export interface UnreadNotificationsResponse {
  notifications: UnreadNotification[];
  total_count: number;
}

class NotificationService {
  private baseURL = `${process.env.NEXT_PUBLIC_API_URL}/v1` || 'http://localhost:8000/api/v1';

  private getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    const refreshToken = localStorage.getItem('refresh_token');
    
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      'X-Refresh-Token': refreshToken || '',
    };
  }

  async markNotificationAsRead(messageId: string, notificationRead: boolean = true): Promise<NotificationResponse> {
    try {
      const response = await axios.put<NotificationResponse>(
        `${this.baseURL}/notifications/${messageId}/mark-read`,
        { notification_read: notificationRead },
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('[NotificationService] Error marking notification as read:', error);
      throw error;
    }
  }

  async markMultipleNotificationsAsRead(messageIds: string[], notificationRead: boolean = true): Promise<NotificationResponse> {
    try {
      const response = await axios.put<NotificationResponse>(
        `${this.baseURL}/notifications/bulk-mark-read`,
        { 
          message_ids: messageIds,
          notification_read: notificationRead 
        },
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('[NotificationService] Error marking multiple notifications as read:', error);
      throw error;
    }
  }

  async getUnreadNotificationsCount(): Promise<UnreadNotificationCount> {
    try {
      const response = await axios.get<UnreadNotificationCount>(
        `${this.baseURL}/notifications/unread-count`,
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('[NotificationService] Error getting unread notifications count:', error);
      throw error;
    }
  }

  async getUnreadNotifications(limit: number = 50): Promise<UnreadNotificationsResponse> {
    try {
      const response = await axios.get<UnreadNotificationsResponse>(
        `${this.baseURL}/notifications/unread?limit=${limit}`,
        {
          headers: this.getAuthHeaders(),
          withCredentials: true,
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('[NotificationService] Error getting unread notifications:', error);
      throw error;
    }
  }
}

export const notificationService = new NotificationService(); 