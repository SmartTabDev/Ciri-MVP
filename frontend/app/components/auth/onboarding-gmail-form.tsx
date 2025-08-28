import React from "react";
import { Button } from "@/components/ui/button";
import { getApiUrl } from "@/lib/utils";
import { Input } from "@/components/ui/input";

const GoogleMailboxIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100px" height="100px" {...props}><path fill="#4caf50" d="M45,16.2l-5,2.75l-5,4.75L35,40h7c1.657,0,3-1.343,3-3V16.2z"/><path fill="#1e88e5" d="M3,16.2l3.614,1.71L13,23.7V40H6c-1.657,0-3-1.343-3-3V16.2z"/><polygon fill="#e53935" points="35,11.2 24,19.45 13,11.2 12,17 13,23.7 24,31.95 35,23.7 36,17"/><path fill="#c62828" d="M3,12.298V16.2l10,7.5V11.2L9.876,8.859C9.132,8.301,8.228,8,7.298,8h0C4.924,8,3,9.924,3,12.298z"/><path fill="#fbc02d" d="M45,12.298V16.2l-10,7.5V11.2l3.124-2.341C38.868,8.301,39.772,8,40.702,8h0 C43.076,8,45,9.924,45,12.298z"/></svg>
);

export const OnboardingGmailForm: React.FC = () => {
  const [appPassword, setAppPassword] = React.useState("");

  React.useEffect(() => {
    if (typeof window !== "undefined") {
      if (appPassword) {
        localStorage.setItem("onboarding_gmail_app_password", appPassword);
      } else {
        localStorage.removeItem("onboarding_gmail_app_password");
      }
    }
  }, [appPassword]);

  const handleGmailConnect = () => {
    window.location.href = getApiUrl() + "/v1/auth/gmail/login?redirect_to=onboarding";
  };

  return (
    <div className="flex flex-col items-center gap-6 mt-8 w-full max-w-sm">
      
      <div className="flex flex-col items-center gap-6 w-full">
        <p className="text-sm text-center">
          Go to your <a className="!text-[#0381fe]" href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener noreferrer">Google account 2FA settings</a> and generate an App Password.
        </p>
        <Input
          type="password"
          placeholder="Enter Gmail app password"
          value={appPassword}
          onChange={e => setAppPassword(e.target.value)}
          className="mb-4"
        />
        <Button
          type="button"
          className="w-full text-base font-semibold bg-white text-[#4285F4] border border-[#4285F4] hover:bg-[#f1f6fd] hover:text-[#1967D2] p-2 shadow-md max-w-32"
          style={{ boxShadow: '0 2px 8px 0 rgba(66,133,244,0.10)', height: 'max-content' }}
          onClick={handleGmailConnect}
          disabled={!appPassword}
        >
          <GoogleMailboxIcon style={{width: 100, height: 100}} />
        </Button>
      </div>
    </div>
  );
}; 