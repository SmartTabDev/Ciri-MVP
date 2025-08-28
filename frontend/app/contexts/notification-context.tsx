'use client';

import React, { createContext, useContext, useState, useCallback, ReactNode, useMemo } from 'react';
import { notificationService } from '@/services/notification-service';

export interface NotificationItem {
  id: string;
  messageId: string;
  chatId: string;
  from: string;
  subject: string;
  content: string;
  actionType: string;
  urgency: string;
  actionReason: string;
  timestamp: Date;
  read: boolean;
}

interface NotificationContextType {
  notifications: NotificationItem[];
  addNotification: (notification: Omit<NotificationItem, 'id' | 'timestamp' | 'read'>) => void;
  markAsRead: (notificationId: string) => void;
  markAllAsRead: () => void;
  removeNotification: (notificationId: string) => void;
  clearAllNotifications: () => void;
  unreadCount: number;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (context === undefined) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider = ({ children }: NotificationProviderProps) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

console.log(notifications)

  const addNotification = useCallback((notification: Omit<NotificationItem, 'id' | 'timestamp' | 'read'>) => {
    console.log("=========>add notification")
    const newNotification: NotificationItem = {
      ...notification,
      id: notification.messageId,
      timestamp: new Date(),
      read: false,
    };

    setNotifications(prev => {
      // Check if notification already exists for this message
      const exists = prev.some(n => n.messageId === notification.messageId);
      if (exists) {
        return prev;
      }
      return [newNotification, ...prev];
    });
  }, []);

  const markAsRead = useCallback(async (notificationId: string) => {
    await notificationService.markNotificationAsRead(notificationId, true);
    setNotifications(prev =>
      prev.map(notification =>
        notification.id === notificationId
          ? { ...notification, read: true }
          : notification
      )
    );
  }, []);

  const markAllAsRead = useCallback(async () => {
    await notificationService.markMultipleNotificationsAsRead(notifications.map(notification => notification.id), true);
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
  }, []);

  const removeNotification = useCallback((notificationId: string) => {
    setNotifications(prev =>
      prev.filter(notification => notification.id !== notificationId)
    );
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const unreadCount = useMemo(() => notifications.filter(n => !n.read).length, [notifications]);

  const value: NotificationContextType = {
    notifications,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAllNotifications,
    unreadCount,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}; 