import React, { useState } from "react";
import axios from "axios";
import { useMotherStore } from "@/stores/motherStore";
import { useChat } from "@/contexts/chat-context";
import { useUser } from "@/contexts/user-context";
import {
  Mic,
  Paperclip,
  PlusCircleIcon,
  SendIcon,
  SmileIcon,
  Play,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { getApiUrl } from "@/lib/utils";
import { ConfirmationModal } from "./confirmation-modal";

export function ChatFooter() {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [showConfirmationModal, setShowConfirmationModal] = useState(false);
  const [modalLoading, setModalLoading] = useState(false);
  const [enableLoading, setEnableLoading] = useState(false);
  const { selectedChatId } = useMotherStore();
  const { chats, setChats, addMessageToExistingChat } = useChat();
  const { user } = useUser();

  const selectedChat = chats.find((c) => c.id === selectedChatId);
  const recipientEmail = selectedChat?.user?.email;
  const subject = selectedChat?.subject;
  const emailProvider = selectedChat?.email_provider || 'gmail';
  const isMeta = emailProvider === 'facebook' || emailProvider === 'instagram';
  const recipientId = selectedChat?.user?.email || (selectedChat as any)?.user?.id || selectedChatId; // fallback for meta

  console.log(selectedChat)

  const handleSend = async () => {
    if (!message.trim()) return;
    if (!isMeta && (!recipientEmail || !subject)) return;
    if (isMeta && !recipientId) return;
    setLoading(true);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      const url = isMeta
        ? (emailProvider === 'facebook' ? "/v1/ai/send-facebook" : "/v1/ai/send-instagram")
        : "/v1/ai/send-email";
      const payload = isMeta
        ? {
            recipient_id: recipientId,
            message: message,
            thread_id: selectedChatId,
          }
        : {
            to: recipientEmail,
            subject: subject,
            body: message,
            thread_id: selectedChatId,
            original_message_id: selectedChat?.messages?.[(selectedChat?.messages?.length ?? 1) - 1]?.id,
          };
      const response = await axios.post(
        getApiUrl() + url,
        payload,
        {
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        }
      );
      if (response.status !== 200) {
        alert(`Failed to send email: ${response.data?.detail || response.statusText}`);
      } else {
        // Create a new message object for the sent email
        const sentMessage = {
          id: response.data?.message_id || `sent-${Date.now()}`,
          from: isMeta ? (emailProvider === 'facebook' ? 'Facebook Page' : 'Instagram') : (user?.company_gmail_box_email || user?.email || 'Unknown'),
          date: new Date().toISOString(),
          content: message,
          read: true, // Mark as read since we sent it
        };
        
        // Add the sent message to the current chat
        if (selectedChatId) {
          addMessageToExistingChat(selectedChatId, sentMessage);
        }
        
        setMessage("");
      }
    } catch (err: any) {
      alert("Error sending email");
    } finally {
      setLoading(false);
    }
  };

  const handleSendClick = () => {
    if (!message.trim()) return;
    if (!isMeta && (!recipientEmail || !subject)) return;
    
    // Check if auto-reply is already disabled for this channel
    const selectedChat = chats.find((c) => c.id === selectedChatId);
    if (selectedChat && selectedChat.enable_auto_reply === false) {
      // Auto-reply is already disabled, send message directly
      handleSend();
    } else {
      // Auto-reply is enabled or undefined, show confirmation modal
      setShowConfirmationModal(true);
    }
  };

  const handleConfirmSend = async () => {
    setModalLoading(true);
    try {
      // First, disable auto-reply for this channel
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      await axios.post(
        getApiUrl() + `/v1/companies/channels/${selectedChatId}/disable-auto-reply`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        }
      );
      
      // Update the chat state to reflect the disabled auto-reply
      setChats((prevChats) => {
        return prevChats.map((chat) => {
          if (chat.id === selectedChatId) {
            return {
              ...chat,
              enable_auto_reply: false,
            };
          }
          return chat;
        });
      });
      
      // Close the modal
      setShowConfirmationModal(false);
      
      // Then send the message
      handleSend();
    } catch (error) {
      console.error("Error disabling auto-reply:", error);
      // Close the modal even if there's an error
      setShowConfirmationModal(false);
      // Still try to send the message even if disabling auto-reply fails
      handleSend();
    } finally {
      setModalLoading(false);
    }
  };

  const handleCancelSend = () => {
    // User cancelled the send operation
    console.log("Send operation cancelled by user");
  };

  const handleEnableAutoReply = async () => {
    if (!selectedChatId) return;
    
    setEnableLoading(true);
    try {
      const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
      await axios.post(
        getApiUrl() + `/v1/companies/channels/${selectedChatId}/enable-auto-reply`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        }
      );
      
      // Update the chat state to reflect the enabled auto-reply
      setChats((prevChats) => {
        return prevChats.map((chat) => {
          if (chat.id === selectedChatId) {
            return {
              ...chat,
              enable_auto_reply: true,
            };
          }
          return chat;
        });
      });
    } catch (error) {
      console.error("Error enabling auto-reply:", error);
      alert("Failed to enable auto-reply");
    } finally {
      setEnableLoading(false);
    }
  };

  return (
    <>
      <div className="lg:px-4">
        <div className="bg-muted relative flex items-center rounded-md border">
          <Input
            type="text"
            className="h-14 border-transparent bg-white pe-32 text-base! shadow-transparent! ring-transparent! lg:pe-56"
            placeholder="Enter message..."
            value={message}
            onChange={e => setMessage(e.target.value)}
            disabled={loading || !recipientEmail || !subject}
          />
          <div className="absolute end-4 flex items-center">
            <div className="block lg:hidden">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="size-11 rounded-full p-0">
                    <PlusCircleIcon className="size-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem>Emoji</DropdownMenuItem>
                  <DropdownMenuItem>Add File</DropdownMenuItem>
                  <DropdownMenuItem>Send Voice</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            <div className="hidden lg:block">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon" className="rounded-full">
                      <SmileIcon />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="top">Emoji</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon" className="rounded-full">
                      <Paperclip />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="top">Select File</TooltipContent>
                </Tooltip>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="ghost" size="icon" className="rounded-full">
                      <Mic />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="top">Send Voice</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
            <Button 
              variant="outline" 
              className="ms-3" 
              onClick={handleSendClick} 
              disabled={loading || !message.trim() || !recipientEmail || !subject}
            >
              <span className="hidden lg:inline">{loading ? "Sending..." : "Send"}</span>{" "}
              <SendIcon className="inline lg:hidden" />
            </Button>
            
            {/* Play button to re-enable auto-reply - only show when auto-reply is disabled */}
            {selectedChat && selectedChat.enable_auto_reply === false && (
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="ms-2 rounded-full"
                      onClick={handleEnableAutoReply}
                      disabled={enableLoading}
                    >
                      {enableLoading ? (
                        <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      ) : (
                        <Play className="h-4 w-4" />
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent side="top">Re-enable AI Auto-Reply</TooltipContent>
                </Tooltip>
              </TooltipProvider>
            )}
          </div>
        </div>
      </div>

      <ConfirmationModal
        isOpen={showConfirmationModal}
        onClose={() => setShowConfirmationModal(false)}
        onConfirm={handleConfirmSend}
        onCancel={handleCancelSend}
        isLoading={modalLoading}
      />
    </>
  );
}
