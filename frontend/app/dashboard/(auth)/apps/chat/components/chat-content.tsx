"use client";

import { useEffect, useRef, useMemo } from "react";
import { ChatMessageProps } from "../types";
import { useMotherStore } from "@/stores/motherStore";
import { useUser } from "@/contexts/user-context";
import { useChat } from "@/contexts/chat-context";
import {
  ChatHeader,
  ChatBubble,
  ChatFooter,
  UserDetailSheet,
} from "@/dashboard/(auth)/apps/chat/components";
import Image from "next/image";
import { toast } from "sonner";

export function ChatContent() {
  const { selectedChatId } = useMotherStore();
  const { user } = useUser();
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const { chats } = useChat();

  // Find the current chat from context
  const currentChat = chats.find((c: any) => c.id === selectedChatId);
  const messages = currentChat?.messages || [];
  // console.log(chats, selectedChatId, currentChat)
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollIntoView(false);
    }
  }, [messages]);

  /* //todo Hvis ingen er lagt til. Legg til bilde eller placeholder her */
  if (!currentChat) {
    return (
      <figure className="hidden h-full items-center justify-center text-center lg:flex">
        <Image
          width={200}
          height={200}
          className="block max-w-sm dark:hidden"
          src={`${process.env.DASHBOARD_BASE_URL}/not-selected-chat.svg`}
          alt="shadcn/ui"
          unoptimized
        />
        <Image
          width={200}
          height={200}
          className="hidden max-w-sm dark:block"
          src={`${process.env.DASHBOARD_BASE_URL}/not-selected-chat-light.svg`}
          alt="shadcn/ui"
        />
      </figure>
    );
  }

  return (
    <div className="bg-background fixed inset-0 z-50 flex h-full flex-col p-4 lg:relative lg:z-10 lg:bg-transparent lg:p-0">
      <ChatHeader user={currentChat.user} />
      <div className="flex-1 overflow-y-auto lg:px-4">
        <div ref={messagesContainerRef}>
          <div className="flex flex-col items-start space-y-10 py-8">
            {messages.length &&
              messages.map((item: ChatMessageProps, key: any) => (
                <ChatBubble message={item} key={key} />
              ))}
          </div>
        </div>
      </div>
      <ChatFooter />
      <UserDetailSheet user={currentChat.user} />
    </div>
  );
}
