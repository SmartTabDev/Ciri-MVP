"use client";
import { Button } from "@/components/ui/button";
import axios from "axios";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuPortal,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";
import { useEffect } from "react";
import { getApiUrl } from "@/lib/utils";

import { FollowUpModal } from "./follow-up-modal";

import { useMotherStore } from "@/stores/motherStore";

interface EditLeadsBulkProps {
  countSelected: number;
  id?: string[];
  name?: string;
  followUp?: any;
  kategori?: string;
}

export function EditLeadsBulk({ countSelected, id }: EditLeadsBulkProps) {
  const { followUpModal, setFollowUpModal } = useMotherStore();

  //todo this is where we send the selected changes to the database. This is bulkedit
  const onChangeCategory = (type: string) => {
    const url = getApiUrl();

    id?.flatMap(async (id) => {
      await axios.put(url + `/leads/${id}`, {
        params: {
          kategori: type,
        },
      });
    });
  };

  useEffect(() => console.log("Ids: ", id), []);

  return (
    <div>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline">
            {countSelected} valgt <ChevronDown />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56 px-4 py-2" align="start">
          <DropdownMenuGroup>
            <DropdownMenuItem onClick={() => setFollowUpModal(!followUpModal)}>
              Endre oppfølgingsintervall
            </DropdownMenuItem>
            <DropdownMenuSub>
              <DropdownMenuSubTrigger>Endre kategorier</DropdownMenuSubTrigger>
              <DropdownMenuPortal>
                <DropdownMenuSubContent className="px-4 py-2">
                  <DropdownMenuItem
                    onClick={() => onChangeCategory("feelgood")}
                  >
                    Feelgood
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onChangeCategory("rebooking")}
                  >
                    Rebooking
                  </DropdownMenuItem>
                </DropdownMenuSubContent>
              </DropdownMenuPortal>
            </DropdownMenuSub>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>

      <FollowUpModal />
    </div>
  );
}
