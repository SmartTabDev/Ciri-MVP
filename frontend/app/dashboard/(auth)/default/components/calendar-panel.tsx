"use client";

import React from "react";
import FullCalendar from "@fullcalendar/react";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const mockEvents = [
  {
    id: "1",
    title: "Team Meeting",
    start: "2024-01-15T10:00:00",
    end: "2024-01-15T11:00:00",
    color: "#3b82f6",
  },
  {
    id: "2",
    title: "Product Launch",
    start: "2024-01-18T14:00:00",
    end: "2024-01-18T16:00:00",
    color: "#10b981",
  },
  {
    id: "3",
    title: "Client Call",
    start: "2024-01-20T09:00:00",
    end: "2024-01-20T10:00:00",
    color: "#f59e0b",
  },
  {
    id: "4",
    title: "Strategy Session",
    start: "2024-01-22T13:00:00",
    end: "2024-01-22T15:00:00",
    color: "#8b5cf6",
  },
  {
    id: "5",
    title: "Review Meeting",
    start: "2024-01-25T11:00:00",
    end: "2024-01-25T12:00:00",
    color: "#ef4444",
  },
];

export function CalendarPanel() {
  const handleDateClick = (arg: any) => {
    console.log("Date clicked:", arg.dateStr);
  };

  const handleEventClick = (arg: any) => {
    console.log("Event clicked:", arg.event.title);
  };

  return (
    <Card className="h-full relative overflow-hidden">
      <CardHeader>
        <CardTitle>Upcoming Events</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <FullCalendar
            plugins={[dayGridPlugin, interactionPlugin]}
            initialView="dayGridMonth"
            headerToolbar={{
              left: "prev,next today",
              center: "title",
              right: "dayGridMonth,dayGridWeek",
            }}
            events={mockEvents}
            dateClick={handleDateClick}
            eventClick={handleEventClick}
            height="100%"
            dayMaxEvents={3}
            moreLinkClick="popover"
            eventDisplay="block"
            eventTimeFormat={{
              hour: "numeric",
              minute: "2-digit",
              meridiem: "short",
            }}
            buttonText={{
              today: "Today",
              month: "Month",
              week: "Week",
            }}
          />
        </div>
      </CardContent>
      
      {/* Blur Overlay */}
      <div className="absolute inset-0 bg-background/60 backdrop-blur-sm flex items-center justify-center z-10">
        <div className="text-center">
          <div className="text-2xl font-bold text-muted-foreground mb-2">Coming Soon...</div>
          <div className="text-sm text-muted-foreground">Event calendar will be available soon</div>
        </div>
      </div>
    </Card>
  );
} 