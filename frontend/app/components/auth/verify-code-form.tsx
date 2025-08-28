import { cn } from "@/lib/utils";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { InputOTP, InputOTPGroup, InputOTPSlot } from "@/components/ui/input-otp";
import { Form, FormField, FormItem, FormControl, FormMessage } from "@/components/ui/form";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Loader2Icon } from "lucide-react";
import { toast } from "@/components/ui/use-toast";
import { useEffect } from "react";
import axios from "axios";
import { getApiUrl } from "@/lib/utils";
import { useRouter } from "next/navigation";

const formSchema = z.object({
  code: z.string().length(6, "Code must be 6 digits").regex(/^\d{6}$/, "Code must be 6 digits"),
});

type FormValues = z.infer<typeof formSchema>;

export function VerifyCodeForm({ className, email, ...props }: React.ComponentProps<"form"> & { email: string }) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resendTimer, setResendTimer] = useState(0);
  const router = useRouter();
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { code: "" },
  });

  useEffect(() => {
    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer(resendTimer - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendTimer]);

  const onSubmit = async (data: FormValues) => {
    setIsSubmitting(true);
    try {
      const res = await axios.post(
        getApiUrl() + "/v1/auth/verify-code",
        {
          email,
          code: data.code,
        },
        { headers: { "Content-Type": "application/json" } }
      );
      const result = res.data;
      if (!res || !res.data || res.status !== 200) {
        toast({
          description: result.detail || result.message || "Verification failed",
          variant: "destructive",
        });
      } else {
        toast({
          description: result.message || "Email verified!",
        });
        setTimeout(() => {
          router.push("/login");
        }, 1500);
      }
    } catch (e: any) {
      toast({
        description: e?.response?.data?.detail ?? "Please check your internet connection.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResend = async (e: React.MouseEvent) => {
    e.preventDefault();
    setResendTimer(30);
    
    try {
      const res = await axios.post(
        getApiUrl() + "/v1/auth/resend-verification-code",
        { email },
        { headers: { "Content-Type": "application/json" } }
      );
      
      if (res.status === 200) {
        toast({ 
          description: res.data.message || "Verification code resent successfully!" 
        });
      } else {
        toast({
          description: res.data.detail || "Failed to resend verification code",
          variant: "destructive",
        });
      }
    } catch (error: any) {
      toast({
        description: error?.response?.data?.detail || "Failed to resend verification code. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <Form {...form}>
      <form className={cn("flex flex-col gap-6", className)} onSubmit={form.handleSubmit(onSubmit)} {...props}>
        <div className="flex flex-col items-center gap-2 text-center">
          <h1 className="font-display text-2xl">Verify Code</h1>
          <p className="font-sans text-sm text-balance">
            Enter the 6-digit code sent to your email address
          </p>
        </div>
        <div className="grid gap-6">
          <FormField
            control={form.control}
            name="code"
            render={({ field }) => (
              <FormItem>
                <FormControl>
                  <InputOTP autoFocus maxLength={6} {...field}>
                    <InputOTPGroup className="w-full justify-center">
                      <InputOTPSlot index={0} />
                      <InputOTPSlot index={1} />
                      <InputOTPSlot index={2} />
                      <InputOTPSlot index={3} />
                      <InputOTPSlot index={4} />
                      <InputOTPSlot index={5} />
                    </InputOTPGroup>
                  </InputOTP>
                </FormControl>
                <FormMessage className="text-center" />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2Icon className="animate-spin" /> Verifying...
              </>
            ) : (
              "Verify Code"
            )}
          </Button>
          <div className="mt-2 text-center text-sm">
            {resendTimer > 0 ? (
              <span className="text-muted-foreground">Resend available in {resendTimer}s</span>
            ) : (
              <a
                href="#"
                className="underline"
                onClick={handleResend}
                aria-disabled={resendTimer > 0}
              >
                Didn&apos;t get a code? Resend
              </a>
            )}
          </div>
        </div>
      </form>
    </Form>
  );
} 