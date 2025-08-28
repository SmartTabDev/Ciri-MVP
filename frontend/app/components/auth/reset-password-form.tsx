import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Form, FormField, FormItem, FormControl, FormMessage } from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2Icon } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import { cn } from "@/lib/utils";
import axios from "axios";
import { getApiUrl } from "@/lib/utils";
import { useRouter, useSearchParams } from "next/navigation";

const formSchema = z
  .object({
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type FormValues = z.infer<typeof formSchema>;

export function ResetPasswordForm({ className }: { className?: string }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { password: "", confirmPassword: "" },
  });

  const onSubmit = async (data: FormValues) => {
    if (!token) {
      toast({
        title: "Invalid or missing reset token.",
        variant: "destructive",
      });
      return;
    }
    setIsSubmitting(true);
    try {
      const res = await axios.post(getApiUrl() + "/v1/auth/reset-password", {
        token,
        new_password: data.password,
      });
      toast({
        title: res.data.message || "Password reset successful!",
        description: "You can now log in with your new password.",
      });
      setTimeout(() => router.replace("/login"), 1500);
    } catch (e: any) {
      toast({
        title: "Reset failed",
        description: e?.response?.data?.detail || "Failed to reset password",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <div className={cn("flex flex-col gap-6", className)}>
        <div className="flex flex-col items-center gap-2 text-center">
          <h1 className="font-display text-2xl">Reset Password</h1>
          <p className="font-sans text-sm text-balance">
            Enter your new password below.
          </p>
        </div>
        <form onSubmit={form.handleSubmit(onSubmit)} className="grid gap-6">
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <Label htmlFor="password">New Password</Label>
                <FormControl>
                  <Input
                    {...field}
                    id="password"
                    type="password"
                    autoComplete="new-password"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="confirmPassword"
            render={({ field }) => (
              <FormItem>
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <FormControl>
                  <Input
                    {...field}
                    id="confirmPassword"
                    type="password"
                    autoComplete="new-password"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2Icon className="animate-spin" /> Resetting...
              </>
            ) : (
              "Reset Password"
            )}
          </Button>
        </form>
      </div>
    </Form>
  );
} 