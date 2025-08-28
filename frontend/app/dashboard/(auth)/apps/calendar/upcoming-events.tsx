import React from "react";

import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { ClockIcon } from "lucide-react";
import { useMotherStore } from "@/stores/motherStore";
import { Badge } from "@/components/ui/badge";
import { eventColors } from "@/dashboard/(auth)/apps/calendar/data";
import { EventInput } from "@fullcalendar/core";

export function UpcomingEvents() {
  const { events, setSelectedEvent, setOpenSheet } = useMotherStore();

  function handleSelectEvent(event: EventInput) {
    setSelectedEvent(event);
    setOpenSheet(true);
  }

  if (events.length === 0) {
    return (
      <div className="text-muted-foreground rounded-md border py-4 text-center text-sm xl:w-72">
        No upcoming events.
      </div>
    );
  }

  return (
    <div className="flex flex-col xl:w-72">
      <h5 className="bg-background sticky top-0 hidden items-center pb-5 font-medium xl:flex">
        Upcoming Events{" "}
        <Badge variant="outline" className="ms-2">
          {events.length} Events
        </Badge>
      </h5>
      <div className="mt-0.5 divide-y overflow-hidden rounded-md xl:border">
        {events.map((event, key: number) => (
          <div
            key={key}
            className={cn(
              "xl:hover:bg-muted cursor-pointer space-y-2 py-4 text-sm xl:px-4",
            )}
            onClick={() => handleSelectEvent(event)}
          >
            <div className="flex items-start gap-2 font-medium">
              <span
                className={cn(
                  "mt-1 block size-4 rounded-full",
                  eventColors[event.color ?? "blue"],
                )}
              ></span>
              <div className="space-y-2">
                <div>{event.title}</div>
                <div className="text-muted-foreground flex items-center gap-1 text-xs">
                  <ClockIcon className="size-3!" />{" "}
                  {format(event.start as Date, "MMM d, yyyy h:mm a")}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
