"use client";

import { Fragment, useEffect } from "react";
import Link from "next/link";
import { page_routes } from "@/lib/routes-config";
import { ChevronRight, ChevronsUpDown } from "lucide-react";
import { usePathname } from "next/navigation";

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Sidebar as SidebarContainer,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  useSidebar,
} from "@/components/ui/sidebar";

import Icon from "@/components/icon-component";
import Logo from "@/components/layout/logo";

import { useIsTablet } from "@/hooks/use-mobile";
import { cn } from "@/lib/utils";
import { useThemeConfig } from "../active-theme";
import Image from "next/image";
import { useChat } from "@/contexts/chat-context";

export default function Sidebar() {
  const pathname = usePathname();
  const { setOpen, setOpenMobile, isMobile, state } = useSidebar();
  const isOpen = state === "collapsed";
  const isTablet = useIsTablet();
  const { theme, setTheme } = useThemeConfig();
  const { totalUnreadCount } = useChat();

  useEffect(() => {
    if (isMobile) setOpenMobile(false);
  }, [pathname]);

  useEffect(() => {
    setOpen(!isTablet);
  }, [isTablet]);

  return (
    <SidebarContainer
      collapsible="icon"
      variant="floating"
      className="bg-background"
    >
      <SidebarHeader className="items-center justify-center pt-3 transition-all group-data-[collapsible=icon]:pt-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuItem className="flex items-center gap-0 rounded-xl px-2 pt-2 group-data-[collapsible=icon]:px-0! hover:bg-transparent hover:text-black dark:hover:text-white">
                  <span
                    className={cn(
                      "via-primary/20 mr-2 flex size-12 shrink-0 items-center justify-center rounded-lg bg-linear-to-tr from-white to-white lg:size-8 dark:bg-white",
                    )}
                  >
                    <Image
                      alt="Ciri logo"
                      src="/thecirilogo.png"
                      width={40}
                      height={40}
                    />
                  </span>

                  <div className="font-display text-[16px] font-semibold group-data-[collapsible=icon]:hidden">
                    ciri
                  </div>
                </SidebarMenuItem>
              </DropdownMenuTrigger>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent className="overflow-hidden">
        <ScrollArea className="h-full">
          {page_routes.map((route, key) => {
            return (
              <div key={key}>
                <SidebarGroup key={key}>
                  <SidebarGroupLabel className="text-xs tracking-wider uppercase">
                    {route.title}
                  </SidebarGroupLabel>
                  <SidebarGroupContent>
                    <SidebarMenu className="space-y-1">
                      {route.items.map((item, key) => (
                        <SidebarMenuItem className="" key={key}>
                          {item.items?.length ? (
                            <Fragment>
                              <div className="hidden group-data-[collapsible=icon]:block">
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <SidebarMenuButton
                                      className={cn(
                                        "hover:text-foreground! hover:bg-[var(--primary)]/10! active:bg-[var(--primary)]/10! active:text-white!",
                                        pathname === item.href && "text-white!",
                                      )}
                                      tooltip={item.title}
                                    >
                                      {item.icon && (
                                        <Icon
                                          name={item.icon}
                                          className="accent-sidebar-foreground size-4"
                                        />
                                      )}
                                      <span>{item.title}</span>
                                      <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                                    </SidebarMenuButton>
                                  </DropdownMenuTrigger>
                                  {item.items?.length ? (
                                    <DropdownMenuContent
                                      side={isMobile ? "bottom" : "right"}
                                      align={isMobile ? "end" : "start"}
                                      className="min-w-48 rounded-lg"
                                    >
                                      <DropdownMenuLabel>
                                        {item.title}
                                      </DropdownMenuLabel>
                                      {item.items.map((item) => (
                                        <DropdownMenuItem
                                          className={cn(
                                            "hover:text-foreground hover:bg-[var(--primary)]/10! active:bg-[var(--primary)]/10! active:text-white!",
                                            pathname === item.href &&
                                              "text-white!",
                                          )}
                                          asChild
                                          key={item.title}
                                        >
                                          <a href={item.href}>{item.title}</a>
                                        </DropdownMenuItem>
                                      ))}
                                    </DropdownMenuContent>
                                  ) : null}
                                </DropdownMenu>
                              </div>
                              <Collapsible className="group/collapsible block group-data-[collapsible=icon]:hidden">
                                <CollapsibleTrigger asChild>
                                  <SidebarMenuButton
                                    className="hover:text-foreground! hover:bg-[var(--primary)]/10! active:bg-[var(--primary)]/10! active:text-white!"
                                    tooltip={item.title}
                                  >
                                    {item.icon && (
                                      <Icon
                                        name={item.icon}
                                        className="accent-sidebar-foreground size-4"
                                      />
                                    )}
                                    <span>{item.title}</span>
                                    <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                                  </SidebarMenuButton>
                                </CollapsibleTrigger>
                                <CollapsibleContent>
                                  <SidebarMenuSub>
                                    {item.items.map((subItem, key) => (
                                      <SidebarMenuSubItem key={key}>
                                        <SidebarMenuSubButton
                                          className={cn(
                                            "hover:text-foreground hover:bg-[var(--primary)]/10 active:bg-[var(--primary)]/10",
                                            pathname === subItem.href &&
                                              "text-white!",
                                          )}
                                          isActive={pathname === subItem.href}
                                          asChild
                                        >
                                          <Link
                                            href={subItem.href}
                                            target={
                                              subItem.newTab ? "_blank" : ""
                                            }
                                          >
                                            {subItem.icon && (
                                              <Icon
                                                name={subItem.icon}
                                                className="accent-sidebar-foreground size-4"
                                              />
                                            )}
                                            <span>{subItem.title}</span>
                                          </Link>
                                        </SidebarMenuSubButton>
                                      </SidebarMenuSubItem>
                                    ))}
                                  </SidebarMenuSub>
                                </CollapsibleContent>
                              </Collapsible>
                            </Fragment>
                          ) : (
                            <SidebarMenuButton
                              className={cn(
                                "hover:text-foreground hover:bg-[var(--primary)]/10 active:bg-[var(--primary)]/10",
                                pathname === item.href && "text-white!",
                              )}
                              asChild
                              tooltip={item.title}
                              isActive={pathname === item.href}
                            >
                              <Link
                                href={item.href}
                                target={item.newTab ? "_blank" : ""}
                              >
                                {item.icon && (
                                  <Icon
                                    name={item.icon}
                                    className="accent-sidebar-foreground size-4"
                                  />
                                )}
                                <span>{item.title}</span>
                              </Link>
                            </SidebarMenuButton>
                          )}
                          {!!item.isComing && (
                            <SidebarMenuBadge className="peer-hover/menu-button:text-foreground opacity-50">
                              Coming
                            </SidebarMenuBadge>
                          )}
                          {!!item.isNew && (
                            <SidebarMenuBadge className="border border-green-400 text-green-600 peer-hover/menu-button:text-green-600">
                              New
                            </SidebarMenuBadge>
                          )}
                          {(!!item.isDataBadge && item.href !== "/dashboard/apps/chat") && (
                            <SidebarMenuBadge className="peer-hover/menu-button:text-foreground">
                              {item.isDataBadge}
                            </SidebarMenuBadge>
                          )}
                          {item.href === "/dashboard/apps/chat" && totalUnreadCount > 0 && (
                            <SidebarMenuBadge className="peer-hover/menu-button:text-foreground">
                              {totalUnreadCount}
                            </SidebarMenuBadge>
                          )}
                        </SidebarMenuItem>
                      ))}
                    </SidebarMenu>
                  </SidebarGroupContent>
                </SidebarGroup>
              </div>
            );
          })}
        </ScrollArea>
      </SidebarContent>
    </SidebarContainer>
  );
}
