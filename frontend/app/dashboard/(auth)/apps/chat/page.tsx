"use client";

import path from "path";
import { ChatItemProps, UserPropsTypes, ChatMessageProps } from "./types";
import { useEffect, useMemo, useRef } from "react";
import { useMotherStore } from "@/stores/motherStore";

import {
  ChatSidebar,
  ChatContent,
} from "@/dashboard/(auth)/apps/chat/components";
import { useUser } from "@/contexts/user-context";
import axios from "axios";
import { useChat } from "@/contexts/chat-context";
import { Loader2 } from "lucide-react";
import { Icons } from "@/components/icons";
import { useSearchParams } from "next/navigation";

function ChatPageContent() {
  const context = useChat();
  const { setSelectedChatId, selectedChatId } = useMotherStore();
  const params = useSearchParams();
  const chatId = params.get("chatId");

  useEffect(() => {
    if (chatId && chatId !== selectedChatId) {
      setSelectedChatId(params.get("chatId"));
    }
  }, [chatId, selectedChatId, setSelectedChatId]);

  const {
    chats,
    loading,
    error,
    hasMore,
    loadingMore = false,
    loadMoreChannels,
  } = context;
  const listRef = useRef<HTMLDivElement>(null);

  // Infinite scroll handler
  useEffect(() => {
    const handleScroll = () => {
      if (!listRef.current || loading || loadingMore || !hasMore) return;
      const { scrollTop, scrollHeight, clientHeight } = listRef.current;
      if (scrollTop + clientHeight >= scrollHeight - 10) {
        loadMoreChannels();
      }
    };
    const ref = listRef.current;
    if (ref) {
      ref.addEventListener("scroll", handleScroll);
    }
    return () => {
      if (ref) {
        ref.removeEventListener("scroll", handleScroll);
      }
    };
  }, [loading, loadingMore, hasMore, loadMoreChannels]);
  // chats is now provided by context

  console.log(chats);
  // Show loader at center if loading and no chats yet
  if (loading && chats.length === 0) {
    return (
      <div className="flex h-[calc(100vh-5.3rem)] w-full items-center justify-center">
        <Loader2 className="text-muted-foreground h-8 w-8 animate-spin" />
      </div>
    );
  }

  // Optionally handle loading/error states here
  return (
    <div className="flex h-[calc(100vh-5.3rem)] w-full">
      <div ref={listRef} className="relative h-full overflow-y-auto">
        <div className="flex min-h-full flex-col">
          <ChatSidebar />
        </div>
      </div>
      <div className="grow">
        <ChatContent />
      </div>
    </div>
  );
}

export default function Page() {
  return <ChatPageContent />;
}
