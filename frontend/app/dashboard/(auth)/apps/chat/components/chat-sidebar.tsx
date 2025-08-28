"use client";

import React from "react";
import { Search, Loader2 } from "lucide-react";

import { ChatItemProps } from "@//dashboard/(auth)/apps/chat/types";
import { useMotherStore } from "@/stores/motherStore";
import { useChat } from "@/contexts/chat-context";

import { Input } from "@/components/ui/input";
import { ChatListItem } from "@/dashboard/(auth)/apps/chat/components/chat-list-item";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ActionDropdown } from "@/dashboard/(auth)/apps/chat/components/action-dropdown";

export function ChatSidebar() {
  const { selectedChatId } = useMotherStore();
  const { chats, loadingMore } = useChat();
  const [filteredChats, setFilteredChats] = React.useState(chats);
  const [search, setSearch] = React.useState("");

  React.useEffect(() => {
    const filteredItems = chats.filter((chat) =>
      chat.user.name.toLowerCase().includes(search.toLowerCase()),
    );
    setFilteredChats(filteredItems);
  }, [search, chats]);
  console.log("=============>", chats);
  return (
    <Card className="h-full w-full flex-1 pb-0 lg:w-96">
      <CardHeader>
        <CardTitle className="font-display text-xl lg:text-2xl">
          Ciri innboksen
        </CardTitle>
        <CardAction>
          <ActionDropdown />
        </CardAction>
        <CardDescription className="relative col-span-2 mt-4 flex w-full items-center">
          <Search className="text-muted-foreground absolute start-4 size-4" />
          <Input
            type="text"
            className="ps-10"
            placeholder="Chats search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </CardDescription>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto p-0">
        <div className="block min-w-0 divide-y">
          {filteredChats.length ? (
            filteredChats.map((chat) => (
              <ChatListItem
                chat={chat}
                key={chat.id}
                active={selectedChatId === chat.id}
                avatar={chat.user.avatar}
              />
            ))
          ) : (
            <div className="text-muted-foreground mt-4 text-center text-sm">
              No chat found
            </div>
          )}
          {loadingMore && (
            <div className="flex items-center justify-center py-4">
              <Loader2 className="text-muted-foreground h-6 w-6 animate-spin" />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
