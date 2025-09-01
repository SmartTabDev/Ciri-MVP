'use client'

import React, { createContext, useState, useContext, ReactNode, useEffect, useCallback } from "react";
import axios from "axios";
import { useUser } from "./user-context";
import { ChatItemProps, ChatMessageProps, UserPropsTypes } from "@/dashboard/(auth)/apps/chat/types";
import { useMotherStore } from "@/stores/motherStore";
import { useNotifications } from "./notification-context";

export type ChatMessage = {
  id: string;
  subject: string;
  from: string;
  date: string;
  notification_read: boolean;
  [key: string]: any;
};

export const ChatContext = createContext<{
  chats: ChatItemProps[];
  setChats: React.Dispatch<React.SetStateAction<ChatItemProps[]>>;
  loading: boolean;
  loadingMore: boolean;
  error: string | null;
  hasMore: boolean;
  loadMoreChannels: () => void;
  ws: WebSocket | null;
  setWs: React.Dispatch<React.SetStateAction<WebSocket | null>>;
  addMessageToChannel: (channelId: number, message: any) => void;
  addMessageToExistingChat: (chatId: string, message: ChatMessageProps, enableAutoReply?: boolean) => void;
  totalUnreadCount: number;
  markChatAsRead: (chatId: string) => void;
} | undefined>(undefined);

// Helper to extract name and email from 'Name <email@domain.com>'
function parseNameAndEmail(from: string): { name: string; email: string } {
  const match = from.match(/^(.*)<(.+)>$/);
  if (match) {
    return {
      name: match[1].trim().replace(/"/g, ""),
      email: match[2].trim(),
    };
  } else {
    return { name: from, email: from };
  }
}

export const ChatProvider = ({ children }: { children: ReactNode }) => {
  const { user } = useUser();
  const [chats, setChats] = useState<ChatItemProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const { selectedChatId } = useMotherStore();
  const { addNotification } = useNotifications();

  // Accepts a newChat (ChatItemProps). If chat with same id exists, update it; else, add newChat.
  const addMessageToChannel = (newChat: any) => {
    console.log("newChat", newChat)
    setChats((prev) => {
      const idx = prev.findIndex((chat: any) => chat.subject === newChat.subject);
      if (idx !== -1) {
        // Remove the original chat and add newChat as the first element
        const updated = prev.filter((_, i) => i !== idx);
        return [newChat, ...updated];
      } else {
        // Add new chat
        return [newChat, ...prev];
      }
    });
  };

  // Add a single message to an existing chat
  const addMessageToExistingChat = (chatId: string, message: ChatMessageProps, enableAutoReply?: boolean) => {
    setChats((prevChats) => {
      return prevChats.map((chat) => {
        if (chat.id === chatId) {
          // Check if message already exists to prevent duplicates
          const messageExists = chat.messages?.some(existingMsg => existingMsg.id === message.id);
          if (messageExists) {
            console.log('[DEBUG] Message already exists, skipping:', message.id);
            return chat; // Return unchanged chat if message already exists
          }
          
          // Add the new message to the existing chat's messages array
          const updatedMessages = [...(chat.messages || []), message];
          
          // Check if this is an action-required message and add notification
          if (message.action_required && message.action_reason && !message.notification_read) {
            const chatItem = prevChats.find(c => c.id === chatId);
            addNotification({
              messageId: message.id,
              chatId: chatId,
              from: message.from,
              subject: chatItem?.subject || 'No Subject',
              content: message.content,
              actionType: message.action_type || 'other',
              urgency: message.urgency || 'medium',
              actionReason: message.action_reason,
            });
          }
          
          return {
            ...chat,
            messages: updatedMessages,
            date: message.date, // Update the chat's last activity date
            enable_auto_reply: enableAutoReply !== undefined ? enableAutoReply : chat.enable_auto_reply,
          };
        }
        return chat;
      });
    });
  };

  // WebSocket connection management
  useEffect(() => {
    if (!user || !user.company_id) return;
    const companyId = user.company_id;
    // Use backend API host for websocket
    let apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://cirinew.onrender.com/api';
    apiBase = apiBase.replace(/\/api$/, '');
    let wsProtocol = apiBase.startsWith('https') ? 'wss' : 'ws';
    let wsHost = apiBase.replace(/^https?:\/\//, '');
    const wsUrl = `${wsProtocol}://${wsHost}/ws/company/${companyId}/email`;
    console.log("[DEBUG][ChatContext] Connecting to WebSocket:", wsUrl);
    
    const socket = new window.WebSocket(wsUrl);
    
    setWs(socket);
    socket.onopen = () => {
      console.log('[DEBUG][ChatContext] WebSocket connection opened:', wsUrl);
    };
    socket.onerror = (err) => {
      console.error('[DEBUG][ChatContext] WebSocket error:', err);
      setWs(null);
    };
    socket.onclose = (event) => {
      console.log('[DEBUG][ChatContext] WebSocket closed:', event);
      setWs(null);
    };
    socket.onmessage = (event) => {
      console.log('[DEBUG][ChatContext] WebSocket message received:', event.data);
      try {
        const msg = JSON.parse(event.data);
            console.log("msg", msg, event.data)
        if (msg.type === "new_email") {
          const email = msg.data;
          const { name, email: parsedEmail } = parseNameAndEmail(email.from);
              
          // Check if this is a replied message (from company email)
          const isRepliedMessage = parsedEmail.toLowerCase() === (user?.company_gmail_box_email || '').toLowerCase() ||
                                  parsedEmail.toLowerCase() === (user?.company_outlook_box_email || '').toLowerCase();
          
          if (isRepliedMessage) {
            // This is a replied message, find the existing chat by channel_id
            const existingChat = chats.find(chat => chat.id === email.channel_id || email.thread_id);
                
                if (existingChat && email.bodies && email.bodies.length > 0) {
                  // Check if this replied message already exists
                  const repliedMessageId = email.id; // Use the actual message_id from backend
                  const messageExists = existingChat.messages?.some(msg => msg.id === repliedMessageId);
                  
                  if (!messageExists) {
                    // Add the replied message to the existing chat
                    const repliedMessage = {
                      id: repliedMessageId,
                      from: email.from,
                      date: email.date,
                      content: email.bodies[0].content || '',
                      html: email.bodies[0].html,
                      action_required: email.action_required || false,
                      action_reason: email.action_reason,
                      action_type: email.action_type,
                      urgency: email.urgency,
                      read: selectedChatId === (email.channel_id || email.thread_id) ? true : (email.bodies[0].read || true),
                    };
                    addMessageToExistingChat(existingChat.id, repliedMessage, email.enable_auto_reply);
                  } else {
                    console.log('[DEBUG] Replied message already exists, skipping:', repliedMessageId);
                  }
                }
              }             else {
              // This is a new incoming message, create new chat or update existing
              const chatId = email.channel_id || email.thread_id || email.id;
              const existingChat = chats.find(chat => chat.id === chatId);
                
                if (existingChat) {
                  // Chat exists, check if any of the new messages are duplicates
                  const newMessages = email.bodies
                    .map((body: any) => ({
                      id: body.message_id || `${chatId}-${body.date}`, // Use message_id from backend, fallback to generated ID
                      from: body.from,
                      date: body.date,
                      content: body.content,
                      html: body.html,
                      action_required: body.action_required || false,
                      action_reason: body.action_reason,
                      action_type: body.action_type,
                      urgency: body.urgency,
                      read: selectedChatId === email.thread_id ? true : body.read,
                      notification_read: body.notification_read,
                    }))
                    .filter((newMsg: any) => {
                      // Check if message already exists
                      const messageExists = existingChat.messages?.some(msg => msg.id === newMsg.id);
                      if (messageExists) {
                        console.log('[DEBUG] Message already exists in existing chat, skipping:', newMsg.id);
                        return false;
                      }
                      return true;
                    });
                  
                  // Add only non-duplicate messages
                    newMessages.forEach((newMsg: any) => {
                    addMessageToExistingChat(chatId, newMsg, email.enable_auto_reply);
                    
                    // Add notification for action-required messages
                    if (newMsg.action_required && newMsg.action_reason && !newMsg.notification_read) {
                      addNotification({
                        messageId: newMsg.id,
                        chatId: chatId,
                        from: newMsg.from,
                        subject: email.subject,
                        content: newMsg.content,
                        actionType: newMsg.action_type || 'other',
                        urgency: newMsg.urgency || 'medium',
                        actionReason: newMsg.action_reason,
                      });
                    }
                    });
                } else {
                  // Create new chat
                  const newChat = {
                    id: chatId,
                    name: name,
                    date: email.date,
                    status: 'sent',
                    is_archive: false,
                    subject: email.subject,
                    messages: email.bodies.map((body: any) => ({
                      id: body.message_id || `${chatId}-${body.date}`, // Use message_id from backend, fallback to generated ID
                      from: body.from,
                      date: body.date,
                      content: body.content,
                      html: body.html,
                      action_required: body.action_required || false,
                      action_reason: body.action_reason,
                      action_type: body.action_type,
                      urgency: body.urgency,
                      read: selectedChatId === (email.channel_id || email.thread_id) ? true : body.read,
                      notification_read: body.notification_read,
                    })),
                    user_id: 1, // or derive from context if needed
                    user: {
                      id: 1,
                      name: name,
                      email: parsedEmail,
                      avatar: email.email_provider || 'gmail', // Use email provider for avatar
                      online_status: "success",
                    },
                    enable_auto_reply: email.enable_auto_reply,
          };
          addMessageToChannel(newChat);
          
          // Add notification for action-required messages in new chat
          email.bodies.forEach((body: any) => {
            if (body.action_required && body.action_reason && !body.notification_read) {
              addNotification({
                messageId: body.message_id || `${chatId}-${body.date}`,
                chatId: chatId,
                from: body.from,
                subject: email.subject,
                content: body.content,
                actionType: body.action_type || 'other',
                urgency: body.urgency || 'medium',
                actionReason: body.action_reason,
              });
            }
          });
                }
              }
        }
      } catch (e) {
        console.error('[DEBUG][ChatContext] Error parsing WebSocket message:', e);
          }
    };
    return () => {
      console.log('[DEBUG][ChatContext] Cleaning up WebSocket connection:', wsUrl);
      socket.close();
    };
  }, [user?.company_id, user?.company_gmail_box_email, user?.company_outlook_box_email, chats, addNotification, selectedChatId]);

  const fetchChats = useCallback(async (pageToFetch = 1) => {
    if (!user?.company_id) return;
    if (pageToFetch === 1) setLoading(true);
    else setLoadingMore(true);
    setError(null);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
      const res = await axios.get(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || "https://cirinew.onrender.com/api"}/v1/companies/${user.company_id}/gmail/channels`,
        {
          params: { page: pageToFetch, page_size: 30 },
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(refreshToken ? { "X-Refresh-Token": refreshToken } : {}),
          },
        }
      );
      const { channels: newChannels, has_more } = res.data;
      // Transform channels to chats here
      const newChats = (newChannels as any[]).map((channel: any, idx: number) => {
        const { name, email: parsedEmail } = parseNameAndEmail(channel.from);
        const user: UserPropsTypes = {
          id: idx + 1,
          name: name,
          email: parsedEmail,
          avatar: channel.email_provider || 'gmail', // Use email provider for avatar
          online_status: "success",
        };
        
        // Transform bodies to include is_sent field based on email address
        const messages = (channel.bodies || []).map((body: any) => ({
          id: body.message_id || `${channel.thread_id}-${body.date}`, // Use message_id from backend, fallback to generated ID
          from: body.from,
          date: body.date,
          content: body.content,
          html: body.html,
          read: body.read,
          action_required: body.action_required || false,
          action_reason: body.action_reason,
          action_type: body.action_type,
          urgency: body.urgency,
          notification_read: body.notification_read,
        }));
        
        // Check for action-required messages and add notifications
        messages.forEach((message: ChatMessageProps) => {
          if (message.action_required && message.action_reason && !message.notification_read) {
            addNotification({
              messageId: message.id,
              chatId: channel.thread_id,
              from: message.from,
              subject: channel.channel || 'No Subject',
              content: message.content,
              actionType: message.action_type || 'other',
              urgency: message.urgency || 'medium',
              actionReason: message.action_reason,
            });
          }
        });

        return {
          id: channel.thread_id, // Use thread_id as the chat ID (backward compatibility)
          name: name,
          date: channel.date,
          status: 'sent' as const,
          is_archive: false,
          subject: channel.channel,
          messages: messages,
          user_id: user.id,
          user,
          enable_auto_reply: channel.enable_auto_reply,
          email_provider: channel.email_provider || 'gmail', // Add email provider information
        };
      });
      setChats((prev) => {
        if (pageToFetch === 1) return newChats;
        // Append only chats that are not already present (by id)
        const existingIds = new Set(prev.map((c: ChatItemProps) => c.id));
        const filtered = newChats.filter((c: ChatItemProps) => !existingIds.has(c.id));
        return [...prev, ...filtered];
      });
      // If backend returns empty chats, set hasMore to false
      if (!newChats || newChats.length === 0) {
        setHasMore(false);
      } else {
        setHasMore(has_more);
      }
    } catch (err: any) {
      setError(err.message || "Unknown error");
      if (pageToFetch === 1) setChats([]);
    } finally {
      if (pageToFetch === 1) setLoading(false);
      else setLoadingMore(false);
    }
  }, [user?.company_id, addNotification]);

  useEffect(() => {
    setPage(1);
    fetchChats(1);
  }, [user?.company_id, fetchChats]);

  useEffect(() => {
    if (selectedChatId) {
      markChatAsRead(selectedChatId)
    }
  }, [selectedChatId])

  const loadMoreChannels = useCallback(() => {
    if (!hasMore || loading) return;
    const nextPage = page + 1;
    setPage(nextPage);
    fetchChats(nextPage);
  }, [hasMore, loading, page, fetchChats]);

  // Calculate total unread messages count across all chats
  const totalUnreadCount = React.useMemo(() => {
    const count = chats.reduce((total, chat) => {
      const unreadInChat = chat.messages?.filter(message => message && !message.read)?.length || 0;
      return total + unreadInChat;
    }, 0);
    
    return count;
  }, [chats]);

  // Function to mark all messages in a chat as read (frontend only)
  const markChatAsRead = async (chatId: string) => {
    try {
      // Find the selected chat
      const selectedChat = chats.find(chat => chat.id === chatId);
      if (!selectedChat) {
        console.log('[DEBUG] Chat not found:', chatId);
        return;
      }

      // Check if the chat has any unread messages
      const hasUnreadMessages = selectedChat.messages?.some(message => !message.read);
      if (!hasUnreadMessages) {
        console.log('[DEBUG] No unread messages in chat:', chatId);
        return;
      }

      console.log('[DEBUG] Marking chat as read:', chatId, 'with', selectedChat.messages?.filter(m => !m.read).length, 'unread messages');

      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const refreshToken = typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
      
      // Update the frontend state to reflect the change
      setChats((prevChats) => {
        return prevChats.map((chat) => {
          if (chat.id === chatId) {
            const updatedMessages = chat.messages?.map(message => ({
              ...message,
              read: true
            })) || [];
            
            return {
              ...chat,
              messages: updatedMessages
            };
          }
          return chat;
        });
      });
      
      // Call the backend API to mark the chat as read
      await axios.put(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || "https://cirinew.onrender.com/api"}/v1/companies/chats/${chatId}/mark-as-read`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
            ...(refreshToken ? { "X-Refresh-Token": refreshToken } : {}),
          },
        }
      );
      
      console.log('[DEBUG] Successfully marked chat as read:', chatId);
    } catch (error) {
      console.error("Error marking chat as read:", error);
    }
  };

  return (
    <ChatContext.Provider value={{ chats, setChats, loading, loadingMore, error, hasMore, loadMoreChannels, ws, setWs, addMessageToChannel, addMessageToExistingChat, totalUnreadCount, markChatAsRead }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}; 