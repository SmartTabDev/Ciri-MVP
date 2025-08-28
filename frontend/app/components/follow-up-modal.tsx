"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { useMotherStore } from "@/stores/motherStore";
import EditLeadsFollowUp from "./edit-leads-bulk-followup";

export function FollowUpModal() {
  const { followUpModal, setFollowUpModal } = useMotherStore();

  return (
    <Dialog open={followUpModal} onOpenChange={setFollowUpModal}>
      <DialogContent>
        <DialogTitle>Endre oppfølginsintervall</DialogTitle>
        <DialogDescription>
          <EditLeadsFollowUp />
        </DialogDescription>
      </DialogContent>
    </Dialog>
  );
}
