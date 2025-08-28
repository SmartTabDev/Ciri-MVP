"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { useMotherStore } from "@/stores/motherStore";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "./ui/badge";
import { Leads } from "@/types/leads";
import Icon from "./icon-component";

export function LeadsCategoryDropdown({ kategori }: Leads) {
  const [stateCategory, setStateCategory] = React.useState(kategori);
  const { setCategory } = useMotherStore();
  setCategory(stateCategory ?? "");

  const categoryMap = {
    feelgood: "feelgood",
    gjenkjøp: "gjenkjøp",
  } as const;

  const iconsMap = {
    feelgood: "HandHeart",
    gjenkjøp: "HandCoins",
  } as const;

  const statusesObj = [
    {
      title: "feelgood",
      category: "feelgood",
    },
    {
      title: "gjenkjøp",
      category: "gjenkjøp",
    },
  ];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline">
          {
            <Badge
              variant={categoryMap[stateCategory as keyof typeof categoryMap]}
            >
              <Icon name={iconsMap[stateCategory as keyof typeof iconsMap]} />
              {stateCategory
                ? stateCategory.replace("-", " ")
                : kategori?.replace("-", " ")}
            </Badge>
          }
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56">
        <DropdownMenuLabel>Kategori</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {statusesObj.map((cat, idx) => (
          <DropdownMenuRadioGroup
            key={idx}
            value={cat.title}
            onValueChange={() =>
              setStateCategory(cat.category as "feelgood" | "gjenkjøp")
            }
          >
            <DropdownMenuRadioItem value={cat.title} key={idx}>
              <Badge
                className="flex items-center gap-1 capitalize"
                variant={categoryMap[cat.category as keyof typeof categoryMap]}
              >
                <Icon name={iconsMap[cat.category as keyof typeof iconsMap]} />
                {cat.category.replace("-", " ")}
              </Badge>
            </DropdownMenuRadioItem>
          </DropdownMenuRadioGroup>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
