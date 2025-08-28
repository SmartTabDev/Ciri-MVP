import { StateCreator } from "zustand";
import { EventInput } from "@fullcalendar/core/index.js";
import { calendarEvents } from "@/dashboard/(auth)/apps/calendar/data";

export interface CalendarSlice {
  events: EventInput[];
  selectedEvent: EventInput | null;
  openSheet: boolean;
  addEvent: (event: EventInput) => void;
  setOpenSheet: (value: boolean) => void;
  setSelectedEvent: (event: EventInput | null) => void;
}

export const createCalendarSlice: StateCreator<
  CalendarSlice,
  [["zustand/immer", never]],
  [],
  CalendarSlice
> = (set) => ({
  events: calendarEvents,
  selectedEvent: null,
  openSheet: false,
  addEvent: (event) =>
    set((state) => {
      state.events.push(event);
    }),
  setOpenSheet: (value) => {
    if (!value) {
      setTimeout(() => {
        set((state) => (state.selectedEvent = null));
      }, 500);
    }
    set((state) => (state.openSheet = value));
  },
  setSelectedEvent: (event) => set((state) => (state.selectedEvent = event)),
});
