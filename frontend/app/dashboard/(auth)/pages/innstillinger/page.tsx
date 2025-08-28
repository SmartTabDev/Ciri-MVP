"use client";

import Link from "next/link";
import { zodResolver } from "@hookform/resolvers/zod";
import { useFieldArray, useForm } from "react-hook-form";
import { z } from "zod";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";

import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Card, CardContent } from "@/components/ui/card";
import { useState, useEffect } from "react";
import { textContextService } from "@/services/text-context-service";
import { useUser } from "@/contexts/user-context";
import { TextContextForm } from "@/components/settings/text-context-form";

const profileFormSchema = z.object({
  instruction: z
    .string()
    .max(1000, {
      message: "Du har overskredet grensen på 1000 ord.",
    })
    .min(100, {
      message: "Du må minst har 100 bokstaver i instruksen til Ciri.",
    }),
});

type ProfileFormValues = z.infer<typeof profileFormSchema>;

// This can come from your database or API.
const defaultValues: Partial<ProfileFormValues> = {
  instruction: "",
};

export default function Page() {
  const { user, loading: userLoading } = useUser();
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [textContext, setTextContext] = useState("");

  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues,
    mode: "onChange",
  });

  const [wordCount, setWordCount] = useState<number>(0);

  // Load text context when component mounts
  useEffect(() => {
    const loadTextContext = async () => {
      if (!user?.company_id || userLoading) return;
      
      setIsLoading(true);
      try {
        const context = await textContextService.getTextContext(user.company_id);
        if (context) {
          setTextContext(context);
          form.setValue('instruction', context);
          setWordCount(textContext.replace(/[^a-zA-ZæøåÆØÅ]/g, "").length);
        }
      } catch (error) {
        console.error('Error loading text context:', error);
        toast.error("Feil ved lasting av kontekst", {
          description: "Kunne ikke laste inn tidligere lagret kontekst",
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadTextContext();
  }, [user?.company_id, userLoading, form]);

  // Update form when textContext changes
  useEffect(() => {
    form.setValue('instruction', textContext);
  }, [textContext, form]);

  async function onSubmit(data: ProfileFormValues) {
    if (!user?.company_id) {
      toast.error("Ingen bedrift funnet", {
        description: "Kunne ikke lagre kontekst uten bedrifts-ID",
      });
      return;
    }

    setIsSaving(true);
    try {
      await textContextService.saveTextContext(user.company_id, data.instruction);
      toast.success("Kontekst lagret", {
        description: "Bedriftskonteksten din er nå lagret",
      });
    } catch (error: any) {
      console.error('Error saving text context:', error);
      toast.error("Feil ved lagring", {
        description: "Kunne ikke lagre kontekst. Prøv igjen senere.",
      });
    } finally {
      setIsSaving(false);
    }
  }

  if (userLoading || isLoading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-4"></div>
            <p className="text-muted-foreground">Laster inn...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="instruction"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <TextContextForm
                      textContext={textContext}
                      setTextContext={setTextContext}
                      placeholder="Gi Ciri så mye informasjon om selskapet ditt som mulig..."
                      label="Om selskapet ditt"
                      description="Legg til all informasjon sentralt til virksomheten din; ting som: garanti, retur osv. Du kan også laste opp en tekstfil."
                      disabled={isSaving}
                      maxLength={1000}
                      minLength={100}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button 
              type="submit" 
              className="dark:text-white"
              disabled={isSaving}
            >
              {isSaving ? "Lagrer..." : "Lagre kontekst"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
