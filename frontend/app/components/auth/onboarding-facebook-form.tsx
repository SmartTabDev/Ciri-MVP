"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { getApiUrl } from "@/lib/utils";
import { toast } from "sonner";

const FacebookIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100px" height="100px" {...props}><linearGradient id="Ld6sqrtcxMyckEl6xeDdMa" x1="9.993" x2="40.615" y1="9.993" y2="40.615" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#2aa4f4"/><stop offset="1" stop-color="#007ad9"/></linearGradient><path fill="url(#Ld6sqrtcxMyckEl6xeDdMa)" d="M24,4C12.954,4,4,12.954,4,24s8.954,20,20,20s20-8.954,20-20S35.046,4,24,4z"/><path fill="#fff" d="M26.707,29.301h5.176l0.813-5.258h-5.989v-2.874c0-2.184,0.714-4.121,2.757-4.121h3.283V12.46 c-0.577-0.078-1.797-0.248-4.102-0.248c-4.814,0-7.636,2.542-7.636,8.334v3.498H16.06v5.258h4.948v14.452 C21.988,43.9,22.981,44,24,44c0.921,0,1.82-0.084,2.707-0.204V29.301z"/></svg>
);

export function OnboardingFacebookForm() {
  const [isConnecting, setIsConnecting] = useState(false);

  const handleFacebookConnect = async () => {
    setIsConnecting(true);
    try {
      // Get Facebook auth URL
      const response = await fetch(`${getApiUrl()}/v1/facebook/auth-url`, {
        headers: {
          "Content-Type": "application/json",
          ...(typeof window !== "undefined" && localStorage.getItem("access_token")
            ? { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
            : {}),
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get Facebook auth URL");
      }

      const data = await response.json();
      
      // Redirect to Facebook auth
      window.location.href = data.facebook_auth_url;
    } catch (error) {
      console.error("Error connecting Facebook:", error);
      toast.error("Failed to connect Facebook", {
        description: "Please try again later.",
      });
    } finally {
      setIsConnecting(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-6 mt-8 w-full max-w-sm">
      
      <div className="flex flex-col items-center gap-6 w-full">
        <p className="text-sm text-center">
          Click the button below to securely connect your Facebook page. You&apos;ll be redirected to Facebook to authorize the connection.
        </p>
        
        <div className="flex flex-col items-center gap-2">
          <Button
            type="button"
            className="w-full text-base font-semibold bg-white text-[#1877F2] border border-[#1877F2] hover:bg-[#f0f8ff] hover:text-[#166FE5] p-2 shadow-md max-w-32"
            style={{ boxShadow: '0 2px 8px 0 rgba(24,119,242,0.10)', height: 'max-content' }}
            onClick={handleFacebookConnect}
            disabled={isConnecting}
          >
            <FacebookIcon style={{width: 100, height: 100}} />
          </Button>
        </div>
      </div>
    </div>
  );
}
