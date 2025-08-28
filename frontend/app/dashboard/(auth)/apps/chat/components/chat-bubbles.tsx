'use client';

import React from "react";

import { ChatMessageProps } from "../types";
import { useUser } from "@/contexts/user-context";
import { format, formatDistanceToNow, isToday, isThisYear, parseISO } from 'date-fns';
import { ChatFeedback } from "@/dashboard/(auth)/default/components/chat-feedback";

// Helper: Regex for URLs
const urlRegex = /(https?:\/\/[^\s]+)/g;
const isImage = (url: string) => /\.(jpeg|jpg|gif|png|webp)$/i.test(url);
const isVideo = (url: string) => /\.(mp4|webm|ogg)$/i.test(url);

function parseEmailText(text: string) {
  const lines = text.split("\n");
  return lines.map((line, i) => {
    const parts = line.split(urlRegex);
    return (
      <div key={i} style={{ marginBottom: 4 }}>
        {parts.map((part, j) => {
          if (urlRegex.test(part)) {
            if (isImage(part)) {
              return (
                <img
                  key={j}
                  src={part}
                  alt="email-img"
                  style={{ maxWidth: "100%", borderRadius: 6, margin: "8px 0" }}
                />
              );
            }
            if (isVideo(part)) {
              return (
                <video
                  key={j}
                  src={part}
                  controls
                  style={{ maxWidth: "100%", borderRadius: 6, margin: "8px 0" }}
                />
              );
            }
            return (
              <a
                key={j}
                href={part}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "#1a73e8", textDecoration: "underline" }}
              >
                {part}
              </a>
            );
          }
          // Detect attachments (e.g., "Attachment: filename.pdf")
          if (/^Attachment: (.+)$/i.test(part)) {
            const filename = part.match(/^Attachment: (.+)$/i)?.[1];
            return (
              <div key={j} style={{ color: "#5f6368", fontStyle: "italic" }}>
                📎 {filename}
              </div>
            );
          }
          return part;
        })}
      </div>
    );
  });
}

function extractEmailAddress(from: string): string | null {
  // Matches: Display Name <email@example.com>
  const match = from.match(/<([^>]+)>/);
  if (match) return match[1].toLowerCase();
  // If no angle brackets, fallback to the whole string if it looks like an email
  if (from && from.includes('@')) return from.trim().toLowerCase();
  return null;
}

// Helper to strip quoted history from email content
function stripQuotedHistory(text: string) {
  // Remove everything from the first reply header (e.g., 'On ... wrote:') onward
  const replyHeaderRegex = /^On .+ wrote:$/m;
  const lines = text.split('\n');
  let result = [];
  let inHistory = false;
  for (let i = 0; i < lines.length; i++) {
    if (replyHeaderRegex.test(lines[i])) {
      break; // Stop at the reply header
    }
    if (!lines[i].startsWith('>')) {
      result.push(lines[i]);
    }
  }
  return result.join('\n').trim();
}

// Helper to strip quoted history from HTML content
function stripQuotedHistoryFromHtml(html: string) {
  if (typeof window === 'undefined') return html;
  const parser = new window.DOMParser();
  const doc = parser.parseFromString(html, 'text/html');
  // Remove all <blockquote> elements (common for quoted replies)
  doc.querySelectorAll('blockquote').forEach(el => el.remove());
  // Remove reply header and everything after
  const replyHeaderDiv = Array.from(doc.querySelectorAll('div')).find(div =>
    /^On .+ wrote:$/.test(div.textContent || '')
  );
  if (replyHeaderDiv) {
    let node: HTMLElement | null = replyHeaderDiv as HTMLElement;
    while (node && node.parentElement && node.parentElement !== doc.body) {
      node = node.parentElement;
    }
    if (node && node.parentElement) {
      // Remove all siblings after the reply header div
      let found = false;
      Array.from(node.parentElement.childNodes).forEach(child => {
        if (child === node) found = true;
        if (found && child.parentNode) child.parentNode.removeChild(child);
      });
    }
  }
  return doc.body.innerHTML;
}

function beautifyDateTime(dateString: string) {
  if (!dateString) return '';
  let date: Date;
  // Try to parse as ISO or RFC2822
  try {
    date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
  } catch {
    return dateString;
  }
  const now = new Date();
  let mainPart = '';
  if (isToday(date)) {
    mainPart = format(date, 'p'); // e.g., 1:10 PM
  } else if (isThisYear(date)) {
    mainPart = format(date, 'MMM d, p'); // e.g., Jul 17, 1:10 PM
  } else {
    mainPart = format(date, 'MMM d, yyyy, p'); // e.g., Jul 17, 2025, 1:10 PM
  }
  const rel = formatDistanceToNow(date, { addSuffix: true });
  // Show relative only if less than 2 days ago
  const msAgo = now.getTime() - date.getTime();
  const showRel = msAgo < 1000 * 60 * 60 * 48;
  return showRel ? `${mainPart} (${rel.replace('about ', '')})` : mainPart;
}

export function ChatBubble({ message }: { message: ChatMessageProps }) {
  const { user } = useUser();
  const companyGmailEmail = (user?.company_gmail_box_email || '').toLowerCase();
  const companyOutlookEmail = (user?.company_outlook_box_email || '').toLowerCase();
  const senderEmail = extractEmailAddress(message.from || '');
  // Determine if message is sent by comparing sender email with company email
  const isSent = senderEmail && (companyGmailEmail || companyOutlookEmail) && (senderEmail === companyGmailEmail || senderEmail === companyOutlookEmail);

  // Beautified bubble style
  const bubbleStyle = {
    background: isSent ? '#e6f0ff' : '#fff',
    borderRadius: 18,
    padding: 18,
    fontFamily: 'Inter, Roboto, Arial, sans-serif',
    fontSize: 16,
    color: '#222',
    whiteSpace: 'pre-wrap' as const,
    border: isSent ? '1.5px solid #b3d1ff' : '1.5px solid #e0e0e0',
    boxShadow: '0 2px 8px rgba(60,64,67,.10)',
    maxWidth: 520,
    margin: !isSent ? '12px 0 12px auto' : '12px auto 12px 0',
    textAlign: 'left' as const,
    position: 'relative' as const,
    minWidth: 220,
    transition: 'background 0.2s',
    wordBreak: 'break-word' as const,
    display: 'flex',
    flexDirection: 'column' as const,
    overflow: 'hidden',
    backgroundBlendMode: isSent ? 'lighten' : undefined,
    opacity: 1,
  };

  const beautifiedDate = beautifyDateTime(message.date);

  // Prefer HTML if available, otherwise use plain text content
  if (message.html) {
    const strippedHtml = stripQuotedHistoryFromHtml(message.html);
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: !isSent ? 'flex-end' : 'flex-start', width: '100%' }}>
        <div style={bubbleStyle} dangerouslySetInnerHTML={{ __html: strippedHtml }} />
        <span style={{ fontSize: 12, color: '#bbb', fontWeight: 400, marginTop: -4 }}>{beautifiedDate}</span>
        {isSent && <ChatFeedback messageId={message.id} />}
      </div>
    );
  }
  const content = message.content || "";
  const strippedContent = stripQuotedHistory(content);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: !isSent ? 'flex-end' : 'flex-start', width: '100%' }}>
      <div style={bubbleStyle}>{parseEmailText(strippedContent)}</div>
      <span style={{ fontSize: 12, color: '#bbb', fontWeight: 400, marginTop: -4 }}>{beautifiedDate}</span>
      {isSent && <ChatFeedback messageId={message.id} />}
    </div>
  );
}
