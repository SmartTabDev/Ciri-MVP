"use client";

import { useEffect } from "react";
import { cn } from "@/lib/utils";
import { ChatItemProps } from "../types";
import { Ellipsis } from "lucide-react";
import { useMotherStore } from "@/stores/motherStore";
import { useChat } from "@/contexts/chat-context";
import { format, isToday, isYesterday, isThisYear, parseISO } from "date-fns";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  ChatUserDropdown,
  MessageStatusIcon,
} from "@/dashboard/(auth)/apps/chat/components";
import { Icons } from "@/components/icons";

interface ChatListItemProps {
  chat: ChatItemProps;
  active: boolean | null;
  avatar?: string;
}

function formatGmailDate(dateString?: string) {
  if (!dateString) return "";
  // Accepts RFC 2822, ISO, and other common formats
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return dateString; // fallback to raw string if invalid
  if (isToday(date)) {
    return format(date, "p"); // e.g., 3:45 PM
  }
  if (isYesterday(date)) {
    return "Yesterday";
  }
  if (isThisYear(date)) {
    return format(date, "MMM d"); // e.g., Apr 27
  }
  return format(date, "MMM d, yyyy"); // e.g., Apr 27, 2023
}

export function ChatListItem({ chat, active, avatar }: ChatListItemProps) {
  const { setSelectedChatId, selectedChatId } = useMotherStore();
  const router = useRouter();

  const handleClick = (chat: ChatItemProps) => {
    setSelectedChatId(chat.id);
    router.push(`?chatId=${chat.id}`);
    // Mark all messages in this chat as read when selected
  };

  // Update unread message count logic for new ChatMessageProps structure
  const unreadMessageCount =
    chat?.messages?.filter((item) => item && !item.read) ?? [];

  return (
    <div
      className={cn(
        "group/item hover:bg-muted relative flex min-w-0 cursor-pointer items-center gap-4 px-6 py-4",
        { "dark:bg-muted! bg-gray-200!": active },
      )}
      onClick={() => handleClick(chat)}
    >
      <div className="flex items-center">
        {avatar === "gmail" ? (
          <span className="mr-2">
            <Icons.gmail className="h-8 w-8" />
          </span>
        ) : avatar === "outlook" ? (
          <span className="mr-2">
            <Icons.outlook className="h-8 w-8" />
          </span>
        ) : avatar === "instagram" ? (
          <span className="mr-2">
            <Icons.instagram className="h-8 w-8" />
          </span>
        ) : avatar === "facebook" ? (
          <span className="mr-2">
            <Icons.facebook className="h-8 w-8" />
          </span>
        ) : (
          avatar && (
            <img
              src={avatar}
              alt="avatar"
              className="mr-2 h-8 w-8 rounded-full"
            />
          )
        )}
      </div>
      <div className="min-w-0 grow">
        <div className="flex items-center justify-between">
          <span className="truncate font-medium">{chat.user?.name}</span>
          <span className="text-muted-foreground flex-none text-xs">
            {formatGmailDate(chat.date)}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <MessageStatusIcon status={chat.status} />
          <span className="text-muted-foreground truncate text-start text-sm">
            {chat.subject}
          </span>
          {/* //todo unread messages needs to be dynamic */}
          {unreadMessageCount.length > 0 && (
            <div className="ms-auto flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-green-500 text-sm text-white">
              {unreadMessageCount.length}
            </div>
          )}
        </div>
      </div>
      <div
        className={cn(
          "absolute end-0 top-0 bottom-0 flex items-center bg-linear-to-l from-50% px-4 opacity-0 group-hover/item:opacity-100",
          { "from-muted": !active },
          { "dark:from-muted from-gray-200": active },
        )}
      >
        <ChatUserDropdown>
          <Button size="icon" variant="outline" className="rounded-full">
            <Ellipsis />
          </Button>
        </ChatUserDropdown>
      </div>
    </div>
  );
}
