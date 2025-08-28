import React from "react";
import { Input } from "./ui/input";
import EditLeadsForm from "./edit-leads-form";
import { Leads } from "@/types/leads";

export default function EditLeads({ kategori, name, email }: Leads) {
  return (
    <div>
      <div className="flex items-center gap-2">
        <EditLeadsForm name={name} email={email} kategori={kategori} />
      </div>
    </div>
  );
}
