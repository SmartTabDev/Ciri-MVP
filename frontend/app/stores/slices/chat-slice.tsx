import { StateCreator } from "zustand";
import { ChatItemProps } from "@/dashboard/(auth)/apps/chat/types";

export interface ChatSlice {
  selectedChatId: string | null;
  showProfileSheet: boolean;
  setSelectedChatId: (id: string | null) => void;
  toggleProfileSheet: (value: boolean) => void;
}

export const createChatSlice: StateCreator<
  ChatSlice,
  [["zustand/immer", never]],
  [],
  ChatSlice
> = (set) => ({
  selectedChatId: null,
  showProfileSheet: false,
  setSelectedChatId(id) {
    set((state) => {
      state.selectedChatId = id;
    });
  },
  toggleProfileSheet(value) {
    set((state) => {
      state.showProfileSheet = value;
    });
  },
});
