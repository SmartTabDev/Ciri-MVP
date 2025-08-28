import { StateCreator } from "zustand";
import { ChatItemProps } from "@/dashboard/(auth)/apps/chat/types";

interface FollowUp {
  intervalFrequency: string;
  intervalDuration: string;
  intervalStart: Date;
}

export interface LeadsSlice {
  name: string;
  category: string;
  email: string;
  followUpModal: boolean;
  followUp: FollowUp;
  setFollowUpModal: (followUpModal: boolean) => void;
  setName: (name: string) => void;
  setCategory: (category: string) => void;
  setEmail: (email: string) => void;
  setFollowUp: (followUp: any) => void;
}

export const createLeadsSlice: StateCreator<
  LeadsSlice,
  [["zustand/immer", never]],
  [],
  LeadsSlice
> = (set) => ({
  name: "",
  category: "",
  followUpModal: false,
  email: "",
  followUp: {
    intervalDuration: "",
    intervalFrequency: "",
    intervalStart: new Date(),
  },
  setName(name) {
    set((state) => {
      state.name = name;
    });
  },
  setCategory(category) {
    set((state) => {
      state.category = category;
    });
  },
  setEmail(email) {
    set((state) => {
      state.email = email;
    });
  },
  setFollowUp(update: Partial<FollowUp>) {
    set((state) => {
      Object.assign(state.followUp, update);
    });
  },
  setFollowUpModal(followUpModal) {
    set((state) => {
      state.followUpModal = followUpModal;
    });
  },
});
