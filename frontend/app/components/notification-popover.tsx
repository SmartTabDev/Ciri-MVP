"use client";

import React, { useState } from "react";
import { Bell, AlertTriangle, Clock, UserCheck, X, Check } from "lucide-react";
import {
  useNotifications,
  NotificationItem,
} from "@/contexts/notification-context";
import { useMotherStore } from "@/stores/motherStore";
import { useRouter } from "next/navigation";
import { formatDistanceToNow } from "date-fns";

export function NotificationPopover() {
  const {
    notifications,
    markAsRead,
    markAllAsRead,
    removeNotification,
    unreadCount,
  } = useNotifications();
  const { setSelectedChatId } = useMotherStore();
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case "appointment":
        return <Clock className="h-4 w-4" />;
      case "refund":
      case "complaint":
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <UserCheck className="h-4 w-4" />;
    }
  };

  const getUrgencyColor = (urgency: string) => {
    switch (urgency) {
      case "high":
        return "text-red-600 bg-red-50 border-red-200";
      case "medium":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "low":
        return "text-blue-600 bg-blue-50 border-blue-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const handleNotificationClick = (notification: NotificationItem) => {
    setSelectedChatId(notification.chatId);
    markAsRead(notification.id);
    router.push(`/dashboard/apps/chat?chatId=${notification.chatId}`);
    setIsOpen(false);
  };

  const handleMarkAllAsRead = () => {
    markAllAsRead();
  };

  const handleRemoveNotification = (
    e: React.MouseEvent,
    notificationId: string,
  ) => {
    e.stopPropagation();
    markAsRead(notificationId);
    removeNotification(notificationId);
  };

  const unreadNotifications = notifications.filter((n) => !n.read);

  return (
    <div className="relative">
      {/* Notification Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative rounded-full p-2 text-gray-600 transition-colors hover:bg-gray-100 hover:text-gray-900"
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs text-white">
            {unreadCount > 99 ? "99+" : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Popover */}
      {isOpen && (
        <div className="absolute right-0 z-50 mt-2 max-h-96 w-80 overflow-hidden rounded-lg border border-gray-200 bg-white shadow-lg">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-200 p-4">
            <h3 className="text-sm font-semibold text-gray-900">
              Notifications {unreadCount > 0 && `(${unreadCount})`}
            </h3>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllAsRead}
                  className="text-xs text-blue-600 hover:text-blue-800"
                >
                  Mark all read
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Notification List */}
          <div className="max-h-80 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-sm text-gray-500">
                No notifications
              </div>
            ) : (
              notifications.map((notification) => (
                <div
                  key={notification.id}
                  onClick={() => handleNotificationClick(notification)}
                  className={`cursor-pointer border-b border-gray-100 p-4 transition-colors hover:bg-gray-50 ${
                    !notification.read ? "bg-blue-50" : ""
                  }`}
                >
                  <div className="flex items-start gap-3">
                    {/* Action Icon */}
                    <div
                      className={`rounded-full p-2 ${getUrgencyColor(notification.urgency)}`}
                    >
                      {getActionIcon(notification.actionType)}
                    </div>

                    {/* Content */}
                    <div className="min-w-0 flex-1">
                      <div className="mb-1 flex items-center justify-between">
                        <p className="truncate text-sm font-medium text-gray-900">
                          {notification.from}
                        </p>
                        <div className="flex items-center gap-1">
                          {!notification.read && (
                            <div className="h-2 w-2 rounded-full bg-blue-500"></div>
                          )}
                          <button
                            onClick={(e) =>
                              handleRemoveNotification(e, notification.id)
                            }
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </div>
                      </div>

                      <p className="mb-1 text-sm font-medium text-gray-900">
                        {notification.subject}
                      </p>

                      <p className="mb-2 line-clamp-2 text-xs text-gray-600">
                        {notification.actionReason}
                      </p>

                      <div className="flex items-center justify-between">
                        <span
                          className={`rounded-full px-2 py-1 text-xs ${getUrgencyColor(notification.urgency)}`}
                        >
                          {notification.actionType.charAt(0).toUpperCase() +
                            notification.actionType.slice(1)}{" "}
                          - {notification.urgency}
                        </span>
                        <span className="text-xs text-gray-400">
                          {formatDistanceToNow(notification.timestamp, {
                            addSuffix: true,
                          })}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Backdrop */}
      {isOpen && (
        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
      )}
    </div>
  );
}
