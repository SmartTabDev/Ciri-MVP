import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Form, FormControl, FormField, FormItem, FormMessage } from "@/components/ui/form";
import { Loader2Icon, MailIcon } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";
import axios from "axios";
import { getApiUrl } from "@/lib/utils";
import { useSearchParams } from "next/navigation";

const formSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
});

type FormValues = z.infer<typeof formSchema>;

export function ForgotPasswordForm({ className }: { className?: string }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const searchParams = useSearchParams();
  const emailParam = searchParams.get("email") || "";
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: emailParam },
  });

  const onSubmit = async (data: FormValues) => {
    setIsSubmitting(true);
    try {
      const res = await axios.post(getApiUrl() + "/v1/auth/forgot-password", { email: data.email });
      setIsSubmitted(true);
      toast({
        title: res.data.message || "If your email is registered, you will receive a password reset email.",
        description: "Check your inbox for a password reset link.",
      });
      // Optionally clear the form
      // form.reset();
    } catch (e: any) {
      toast({
        title: "Request failed",
        description: e?.response?.data?.message || "Failed to submit request",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <form className={cn("flex flex-col gap-6", className)} onSubmit={form.handleSubmit(onSubmit)}>
        <div className="flex flex-col items-center gap-2 text-center">
          <h1 className="font-display text-2xl">Forgot Password</h1>
          <p className="font-sans text-sm text-balance">
            Enter your email address and we&apos;ll send you instructions to reset your password.
          </p>
        </div>
        <div className="grid gap-6">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <Label htmlFor="email" className="sr-only">
                  Email address
                </Label>
                <FormControl>
                  <div className="relative">
                    <MailIcon className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 transform opacity-30" />
                    <Input
                      {...field}
                      id="email"
                      type="email"
                      autoComplete="email"
                      className="w-full pl-10"
                      placeholder="Enter your email address"
                    />
                  </div>
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2Icon className="animate-spin" /> Please wait
              </>
            ) : (
              "Send Reset Instructions"
            )}
          </Button>
        </div>
        <div className="text-center text-sm">
          Remembered your password? {""}
          <a href="/login" className="underline underline-offset-4">
            Log in
          </a>
        </div>
      </form>
    </Form>
  );
} 