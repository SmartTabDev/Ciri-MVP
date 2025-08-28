export type ChatItemProps = {
  id: string;
  name?: string;
  image?: string;
  date?: string;
  status?: "sent" | "forwarded" | "read";
  is_archive?: boolean;
  subject?: string;
  messages?: ChatMessageProps[];
  user_id: number;
  user: UserPropsTypes;
  enable_auto_reply?: boolean;
  email_provider?: 'gmail' | 'outlook' | 'smtp';  // Add email provider information
};

export type ChatMessageProps = {
  id: string;
  from: string;
  date: string;
  content: string;
  html?: string;
  read: boolean;
  action_required?: boolean;
  action_reason?: string;
  action_type?: string;
  notification_read?: boolean;
  urgency?: string;
};

export type ChatMessageDataProps = {
  file_name?: string;
  cover?: string;
  path?: string;
  duration?: string;
  size?: string;
  images?: [];
  // For email messages
  email_subject?: string;
  email_from?: string;
  email_date?: string;
};

export type UserPropsTypes = {
  id: number;
  name: string;
  avatar?: string;
  about?: string;
  phone?: string;
  country?: string;
  email?: string;
  gender?: string;
  website?: string;
  online_status?: "success" | "warning" | "danger";
  last_seen?: string;
  social_links?: {
    name?: string;
    url?: string;
  }[];
  medias?: {
    type?: string;
    path?: string;
  }[];
};

export type MediaListItemType = {
  type: string;
};

export type MessageStatusIconType = {
  status?: string;
};
