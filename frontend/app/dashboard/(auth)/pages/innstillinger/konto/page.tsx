"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CalendarIcon, CaretSortIcon, CheckIcon } from "@radix-ui/react-icons";
import { format } from "date-fns";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useState, useEffect } from "react";
import { toast } from "sonner";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Card, CardContent } from "@/components/ui/card";
import { LogoUpload } from "@/components/logo-upload";
import { Textarea } from "@/components/ui/textarea";
import { companyService, CompanyData } from "@/services/company-service";
import { useUser } from "@/contexts/user-context";

const languages = [
  { label: "English", value: "en" },
  { label: "French", value: "fr" },
  { label: "German", value: "de" },
  { label: "Spanish", value: "es" },
  { label: "Portuguese", value: "pt" },
  { label: "Russian", value: "ru" },
  { label: "Japanese", value: "ja" },
  { label: "Korean", value: "ko" },
  { label: "Chinese", value: "zh" },
] as const;

const accountFormSchema = z.object({
  name: z
    .string()
    .min(2, {
      message: "Name must be at least 2 characters.",
    })
    .max(30, {
      message: "Name must not be longer than 30 characters.",
    }),
  dob: z.date({
    required_error: "A date of birth is required.",
  }),
  language: z.string({
    required_error: "Please select a language.",
  }),
});

type AccountFormValues = z.infer<typeof accountFormSchema>;

export default function Page() {
  const { user, loading: userLoading } = useUser();
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);

  const form = useForm<AccountFormValues>({
    resolver: zodResolver(accountFormSchema),
    defaultValues: {
      name: "",
      dob: new Date(),
      language: "",
    },
  });

  // Load company data when component mounts
  useEffect(() => {
    const loadCompanyData = async () => {
      if (!user?.company_id || userLoading) return;
      
      setIsLoading(true);
      try {
        const data = await companyService.getCompany(user.company_id);
        setCompanyData(data);
        
        // Update form with company data
        form.setValue("name", data.name);
        form.setValue("language", data.terms_of_service);
      } catch (error) {
        console.error("Error loading company data:", error);
        toast.error("Kunne ikke laste bedriftsinformasjon");
      } finally {
        setIsLoading(false);
      }
    };

    loadCompanyData();
  }, [user?.company_id, userLoading, form]);

  async function onSubmit(data: AccountFormValues) {
    if (!user?.company_id) {
      toast.error("Ingen bedrift funnet");
      return;
    }

    setIsSaving(true);
    try {
      const updatedCompany = await companyService.updateCompany(user.company_id, {
        name: data.name,
        terms_of_service: data.language, // Using language field for terms_of_service
      });

      setCompanyData(updatedCompany);
      toast.success("Bedriftsinformasjon oppdatert");
    } catch (error: any) {
      console.error("Error updating company:", error);
      const errorMessage = error.response?.data?.detail || "Det oppstod en feil ved oppdatering";
      toast.error(errorMessage);
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <Card className="flex">
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="dob"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Logo</FormLabel>
                  <LogoUpload />

                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Firmanavn</FormLabel>
                  <FormControl>
                    <Input placeholder="Navnet på selskapet" {...field} disabled={isSaving} />
                  </FormControl>
                  <FormDescription>
                    Dette er navnet til selskapet Ciri &quot;jobber for&quot;.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="language"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Vilkår</FormLabel>
                  <Textarea
                    placeholder="Her skriver du inn viktige vilkår og retningslinjer"
                    className="h-[200px]"
                    {...field}
                    disabled={isSaving}
                  />
                  <FormDescription>
                    Informasjonen bistår i konteksten til Ciri
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="dark:text-white" disabled={isSaving}>
              {isSaving ? "Lagrer..." : "Lagre oppdateringer"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
