export enum MessageChannel {
  SMS = "sms",
}

export type MessageChannelType = `${MessageChannel}`;

export interface MessageChannelDetail {
  name: string;
  icon: string; // Iconify icon name
}

// @iconify-include
export const MessageChannelDetails: Record<
  MessageChannelType,
  MessageChannelDetail
> = {
  [MessageChannel.SMS]: { name: "Instruks", icon: "mynaui:chat-messages" },
};

export function getMessageChannelDetails(channel: MessageChannelType) {
  return MessageChannelDetails[channel];
}
