import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Icons } from "@/components/icons";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import {
  Form,
  FormField,
  FormItem,
  FormControl,
  FormMessage,
} from "@/components/ui/form";
import { useState } from "react";
import { toast } from "@/components/ui/use-toast";
import { Loader2Icon } from "lucide-react";
import axios from "axios";
import { getApiUrl } from "@/lib/utils";
import { useRouter } from "next/navigation";
import PasswordInput from "../password-input";

//https://react-hook-form.com/docs/usecontroller/controller
const formSchema = z
  .object({
    email: z.string().email("Please enter a valid email address"),
    password: z.string().min(8, "Password must be at least 8 characters"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passordene er ikke like",
    path: ["confirmPassword"],
  });

type FormValues = z.infer<typeof formSchema>;

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<"form">) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: "", password: "", confirmPassword: "" },
  });
  const router = useRouter();

  const onSubmit = async (data: FormValues) => {
    setIsSubmitting(true);
    try {
      const res = await axios.post(
        getApiUrl() + "/v1/auth/register",
        {
          email: data.email,
          password: data.password,
        },
        { headers: { "Content-Type": "application/json" } },
      );
      const result = res.data;
      if (!res || !res.data || res.status !== 201) {
        if (result.detail) {
          form.setError("email", { message: result.detail });
          form.setError("password", { message: result.detail });
          toast({
            title: result.detail,
            description: "Please check your email and password.",
            variant: "destructive",
          });
        } else if (result.message) {
          toast({
            title: result.message,
            description: "Please check your email and password.",
            variant: "destructive",
          });
        } else {
          toast({
            title: "Signup failed",
            description: "Please check your email and password.",
            variant: "destructive",
          });
        }
      } else {
        toast({
          title:
            result.message ||
            "Signup successful! Please check your email for verification.",
          description: "Please check your email for verification.",
        });
        setTimeout(() => {
          router.push(`/verify-code?email=${encodeURIComponent(data.email)}`);
        }, 1500);
        // Optionally redirect here
      }
    } catch (e: any) {
      toast({
        title: e?.response?.statusText ?? "Network error",
        description:
          e?.response?.data?.detail ?? "Please check your internet connection.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <form
        className={cn("flex flex-col gap-6", className)}
        onSubmit={form.handleSubmit(onSubmit)}
        {...props}
      >
        <div className="flex flex-col items-center gap-2 text-center">
          <h1 className="font-display text-2xl">Velkommen til Ciri</h1>
          <p className="text-muted-foreground font-sans text-sm text-balance">
            Automatiser kundekommunikasjonen
          </p>
        </div>
        <div className="grid gap-6">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <Label htmlFor="email">Email</Label>
                <FormControl>
                  <Input
                    className="rounded-[5px]!"
                    id="email"
                    type="email"
                    placeholder="m@example.com"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                {/* <Label htmlFor="password">Password</Label> */}
                <FormControl>
                  <PasswordInput {...field} />
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
                <Label htmlFor="confirm-password">Confirm Password</Label>
                <FormControl>
                  <Input
                    className="rounded-[5px]!"
                    id="confirm-password"
                    type="password"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button
            type="submit"
            className="w-full dark:text-white"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <Loader2Icon className="mr-2 h-4 w-4 animate-spin" />
                Signing up...
              </>
            ) : (
              "Sign up"
            )}
          </Button>
        </div>
        <div className="after:border-border relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t">
          <span className="bg-background text-muted-foreground relative z-10 px-2">
            Or continue with
          </span>
        </div>
        <Button
          variant="outline"
          className="w-full"
          type="button"
          onClick={() => {
            window.location.href = getApiUrl() + "/v1/auth/google/login";
          }}
        >
          {/* Google Icon */}
          <Icons.google className="mr-2 h-4 w-4" />
          Sign up with Google
        </Button>
        <div className="text-center text-sm">
          Already have an account?{" "}
          <a href="/login" className="underline underline-offset-4">
            Login
          </a>
        </div>
      </form>
    </Form>
  );
}
