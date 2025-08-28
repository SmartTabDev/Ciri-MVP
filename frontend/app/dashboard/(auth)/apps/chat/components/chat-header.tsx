"use client";

import React from "react";
import { ArrowLeft, Ellipsis } from "lucide-react";
import { Button } from "@/components/ui/button";
import { generateAvatarFallback } from "@/lib/utils";

import { useMotherStore } from "@/stores/motherStore";

import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  CallDialog,
  ChatUserDropdown,
  VideoCallDialog,
} from "@/dashboard/(auth)/apps/chat/components";
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  AvatarIndicator,
} from "@/components/ui/avatar";
import { UserPropsTypes } from "@/dashboard/(auth)/apps/chat/types";
import { Icons } from "@/components/icons";

export function ChatHeader({ user }: { user: UserPropsTypes }) {
  const { setSelectedChatId } = useMotherStore();

  return (
    <div className="flex justify-between gap-4 lg:px-4">
      <div className="flex gap-4">
        <Button
          size="sm"
          variant="outline"
          className="flex size-10 p-0 lg:hidden"
          onClick={() => setSelectedChatId(null)}
        >
          <ArrowLeft />
        </Button>
        {/* Avatar logic as in ChatListItem */}
        <div className="flex items-center">
          {user.avatar === 'gmail' ? (
            <span className="mr-2"><Icons.gmail className="w-10 h-10" /></span>
          ) : user.avatar === 'outlook' ? (
            <span className="mr-2"><Icons.outlook className="w-10 h-10" /></span>
          ) : user.avatar === 'instagram' ? (
            <span className="mr-2"><Icons.instagram className="w-10 h-10" /></span>
          ) : user.avatar === 'facebook' ? (
            <span className="mr-2"><Icons.facebook className="w-10 h-10" /></span>
          ) : (
            user.avatar && <img src={user.avatar} alt="avatar" className="w-10 h-10 rounded-full mr-2" />
          )}
        </div>
        <div className="flex flex-col">
          <span className="font-semibold">{user.name}</span>
          {user.online_status == "success" ? (
            <span className="text-sm text-green-500">Online</span>
          ) : (
            <span className="text-muted-foreground text-sm">
              {user.last_seen}
            </span>
          )}
        </div>
      </div>
      <div className="flex gap-2">
        <div className="hidden lg:flex lg:gap-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <div>
                  <VideoCallDialog />
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom">Start Video Chat</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <div>
                  <CallDialog />
                </div>
              </TooltipTrigger>
              <TooltipContent side="bottom">Start Call</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        <ChatUserDropdown>
          <Button size="icon" variant="ghost">
            <Ellipsis />
          </Button>
        </ChatUserDropdown>
      </div>
    </div>
  );
}
