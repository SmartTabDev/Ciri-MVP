import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Icons } from "@/components/icons";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Form, FormField, FormItem, FormControl, FormMessage } from "@/components/ui/form";
import { useState } from "react";
import { toast } from "@/components/ui/use-toast";
import { Loader2Icon } from "lucide-react";
import axios from "axios";
import { getApiUrl } from "@/lib/utils";
import { useRouter } from "next/navigation";

const formSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type FormValues = z.infer<typeof formSchema>;

export function LoginForm({ className, ...props }: React.ComponentProps<"form">) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: "", password: "" },
  });
  const router = useRouter();

  const onSubmit = async (data: FormValues) => {
    setIsSubmitting(true);
    try {
      const res = await axios.post(
        getApiUrl() + "/v1/auth/login",
        new URLSearchParams({
          username: data.email,
          password: data.password,
        }),
        { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
      );
      const result: any = res.data;
      console.log(res)
      if (!res || !res.data || res.status !== 200) {
        if (result.detail) {
          console.log(result)
          form.setError("email", { message: result.detail });
          form.setError("password", { message: result.detail });
          toast({
            title: result.detail,
            description: result.detail,
            variant: "destructive",
          });
        } else if (result.message) {
          toast({
            title: result.message,
            description: result.message,
            variant: "destructive",
          });
        } else {
          toast({
            title: "Login failed",
            description: "Login failed",
            variant: "destructive",
          });
        }
      } else {
        localStorage.setItem("access_token", result.access_token);
        localStorage.setItem("refresh_token", result.refresh_token);
       
        setTimeout(() => {
          router.push("/");
        }, 1000);
      }
    } catch (e: any) {
      toast({
        title: e?.response?.statusText ?? "Network error",
        description: e?.response?.data?.detail ?? "Please check your internet connection.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Form {...form}>
      <form className={cn("flex flex-col gap-6", className)} onSubmit={form.handleSubmit(onSubmit)} {...props}>
        <div className="flex flex-col items-center gap-2 text-center">
          <h1 className="font-display text-2xl">Login to your account</h1>
          <p className="font-sans text-sm text-balance">
            Enter your email below to login to your account
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
                <div className="flex items-center">
                  <Label htmlFor="password">Password</Label>
                  <a
                    href="#"
                    className="ml-auto text-sm underline-offset-4 hover:underline"
                    onClick={e => {
                      e.preventDefault();
                      const email = form.getValues("email");
                      router.push(`/forgot-password${email ? `?email=${encodeURIComponent(email)}` : ""}`);
                    }}
                  >
                    Forgot your password?
                  </a>
                </div>
                <FormControl>
                  <Input
                    className="rounded-[5px]!"
                    id="password"
                    type="password"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2Icon className="animate-spin mr-2 h-4 w-4" />
                Logging in...
              </>
            ) : (
              "Login"
            )}
          </Button>
        </div>
        <div className="after:border-border relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t">
          <span className="bg-background text-muted-foreground relative z-10 px-2">
            Or continue with
          </span>
        </div>
        <Button variant="outline" className="w-full" type="button" onClick={() => {
          window.location.href = getApiUrl() + "/v1/auth/google/login";
        }}>
          {/* Google Icon */}
          <Icons.google className="mr-2 h-4 w-4" />
          Login with Google
        </Button>
        <div className="text-center text-sm">
          Don&apos;t have an account?{" "}
          <a href="/signup" className="underline underline-offset-4">
            Sign up
          </a>
        </div>
      </form>
    </Form>
  );
}
