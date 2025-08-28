"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CalendarIcon, CaretSortIcon, CheckIcon } from "@radix-ui/react-icons";
import { format } from "date-fns";
import { useForm } from "react-hook-form";
import { z } from "zod";

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
import { toast } from "@/components/ui/use-toast";
import { Card, CardContent } from "@/components/ui/card";

import { LeadsUpload } from "@/components/leads-upload";
import { LeadsCategoryDropdown } from "@/components/leads-category-dropdown";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DateInput } from "@heroui/react";
import { FollowUpInput } from "@/components/follow-up-date-input";

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

// This can come from your database or API.
const defaultValues: Partial<AccountFormValues> = {
  // name: "Your name",
  // dob: new Date("2023-01-23"),
};

export default function Page() {
  const form = useForm<AccountFormValues>({
    resolver: zodResolver(accountFormSchema),
    defaultValues,
  });

  function onSubmit(data: AccountFormValues) {
    toast({
      title: "You submitted the following values:",
      description: (
        <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
      ),
    });
  }

  return (
    <div className="relative">
      <Card className="flex blur-sm pointer-events-none">
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
              <FormField
                control={form.control}
                name="dob"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Last opp lister med leads</FormLabel>
                    <LeadsUpload />

                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Kategori</FormLabel>
                    <FormControl>
                      <LeadsCategoryDropdown kategori="feelgood" />
                    </FormControl>
                    <FormDescription className="text-muted-foreground/60 text-xs text-pretty">
                      Dette beskriver formålet for oppfølging. Feelgood er en
                      vennlig oppfølging med formål om kundetilfedshet; Gjenkjøp
                      gir Ciri formålet om å være mest mulig spesifikk for å få
                      kunden til å handle på ny.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormControl>
                <div className="flex flex-wrap items-center gap-2 text-sm text-nowrap">
                  <span>Følg opp</span>
                  <Select>
                    <SelectTrigger className="w-fit">
                      <SelectValue placeholder="hver" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="every">hver</SelectItem>
                      <SelectItem value="every-other">annenhver</SelectItem>
                      <SelectItem value="every-3rd">hver tredje</SelectItem>
                    </SelectContent>
                  </Select>

                  <Select>
                    <SelectTrigger className="w-fit">
                      <SelectValue placeholder="måned" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="year">år</SelectItem>
                      <SelectItem value="month">måned</SelectItem>
                      <SelectItem value="week">uke</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex items-center gap-2">
                    <span>f.om</span>

                    {/* TODO fiks problemet med "falling" opp og ned ved pagination */}
                    <FollowUpInput />
                  </div>
                </div>
              </FormControl>
              <Button type="submit" className="dark:text-white">
                Lagre oppdateringer
              </Button>
            </form>
          </Form>
        </CardContent>
      </Card>
      
      {/* Coming Soon Overlay */}
      <div className="absolute inset-0 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Coming Soon...
          </h2>
          <p className="text-gray-600 dark:text-gray-300">
            This feature is under development
          </p>
        </div>
      </div>
    </div>
  );
}
