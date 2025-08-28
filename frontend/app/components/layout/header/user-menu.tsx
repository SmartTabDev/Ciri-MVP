import { BadgeCheck, Bell, CreditCard, LogOut, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useUser } from "@/contexts/user-context";
import { companyService, CompanyData } from "@/services/company-service";

export default function UserMenu() {
  const { user, logout } = useUser();
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  // Fetch company data when component mounts
  useEffect(() => {
    const loadCompanyData = async () => {
      if (!user?.company_id) return;
      
      setIsLoading(true);
      try {
        const data = await companyService.getCompany(user.company_id);
        setCompanyData(data);
      } catch (error) {
        console.error("Error loading company data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadCompanyData();
  }, [user?.company_id]);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Avatar>
          <AvatarImage
            src={companyData?.logo_url || `${process.env.ASSETS_URL}/avatars/01.png`}
            alt={companyData?.name || "Company"}
          />
          <AvatarFallback className="rounded-lg">
            {companyData?.name ? companyData.name.substring(0, 2).toUpperCase() : "TB"}
          </AvatarFallback>
        </Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        className="w-(--radix-dropdown-menu-trigger-width) min-w-60"
        align="end"
      >
        <DropdownMenuLabel className="p-0">
          <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
            <Avatar>
              <AvatarImage
                src={companyData?.logo_url || `${process.env.ASSETS_URL}/avatars/01.png`}
                alt={companyData?.name || "Company"}
              />
              <AvatarFallback className="rounded-lg">
                {companyData?.name ? companyData.name.substring(0, 2).toUpperCase() : "CN"}
              </AvatarFallback>
            </Avatar>
            <div className="grid flex-1 text-left text-sm leading-tight">
              <span className="truncate font-semibold">
                {companyData?.name || "Company"}
              </span>
              <span className="text-muted-foreground truncate text-xs">
                {user?.username || user?.email || "User"}
              </span>
            </div>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem onClick={() => router.push('/dashboard/pages/innstillinger/konto')}>
            <BadgeCheck />
            Account
          </DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={logout}>
          <LogOut />
          <span style={{ cursor: "pointer" }}>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
