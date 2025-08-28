import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import {
  ApplicationSlice,
  createApplicationSlice,
} from "./slices/application-slice";
import { CalendarSlice, createCalendarSlice } from "./slices/calendar-slice";
import { ChatSlice, createChatSlice } from "./slices/chat-slice";
import { createLeadsSlice, LeadsSlice } from "./slices/leads-slice";

export type RootState = ApplicationSlice &
  CalendarSlice &
  ChatSlice &
  LeadsSlice;

export const useMotherStore = create<RootState>()(
  immer((...args) => ({
    ...createApplicationSlice(...args),
    ...createCalendarSlice(...args),
    ...createChatSlice(...args),
    ...createLeadsSlice(...args),
  })),
);
