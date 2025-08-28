"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { getApiUrl } from "@/lib/utils";
import { toast } from "sonner";

const InstagramIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="100px" height="100px" {...props}><radialGradient id="yOrnnhliCrdS2gy~4tD8ma" cx="19.38" cy="42.035" r="44.899" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fd5"/><stop offset=".328" stop-color="#ff543f"/><stop offset=".348" stop-color="#fc5245"/><stop offset=".504" stop-color="#e64771"/><stop offset=".643" stop-color="#d53e91"/><stop offset=".761" stop-color="#cc39a4"/><stop offset=".841" stop-color="#c837ab"/></radialGradient><path fill="url(#yOrnnhliCrdS2gy~4tD8ma)" d="M34.017,41.99l-20,0.019c-4.4,0.004-8.003-3.592-8.008-7.992l-0.019-20 c-0.004-4.4,3.592-8.003,7.992-8.008l20-0.019c4.4-0.004,8.003,3.592,8.008,7.992l0.019,20 C42.014,38.383,38.417,41.986,34.017,41.99z"/><radialGradient id="yOrnnhliCrdS2gy~4tD8mb" cx="11.786" cy="5.54" r="29.813" gradientTransform="matrix(1 0 0 .6663 0 1.849)" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#4168c9"/><stop offset=".999" stop-color="#4168c9" stop-opacity="0"/></radialGradient><path fill="url(#yOrnnhliCrdS2gy~4tD8mb)" d="M34.017,41.99l-20,0.019c-4.4,0.004-8.003-3.592-8.008-7.992l-0.019-20 c-0.004-4.4,3.592-8.003,7.992-8.008l20-0.019c4.4-0.004,8.003,3.592,8.008,7.992l0.019,20 C42.014,38.383,38.417,41.986,34.017,41.99z"/><path fill="#fff" d="M24,31c-3.859,0-7-3.14-7-7s3.141-7,7-7s7,3.14,7,7S27.859,31,24,31z M24,19c-2.757,0-5,2.243-5,5 s2.243,5,5,5s5-2.243,5-5S26.757,19,24,19z"/><circle cx="31.5" cy="16.5" r="1.5" fill="#fff"/><path fill="#fff" d="M30,37H18c-3.859,0-7-3.14-7-7V18c0-3.86,3.141-7,7-7h12c3.859,0,7,3.14,7,7v12 C37,33.86,33.859,37,30,37z M18,13c-2.757,0-5,2.243-5,5v12c0,2.757,2.243,5,5,5h12c2.757,0,5-2.243,5-5V18c0-2.757-2.243-5-5-5H18z"/></svg>
);

export function OnboardingInstagramForm() {
  const [isConnecting, setIsConnecting] = useState(false);

  const handleInstagramConnect = async () => {
    setIsConnecting(true);
    try {
      // Get Instagram auth URL
      const response = await fetch(`${getApiUrl()}/v1/instagram/auth-url`, {
        headers: {
          "Content-Type": "application/json",
          ...(typeof window !== "undefined" && localStorage.getItem("access_token")
            ? { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
            : {}),
        },
      });

      if (!response.ok) {
        throw new Error("Failed to get Instagram auth URL");
      }

      const data = await response.json();
      
      // Redirect to Instagram auth
      window.location.href = data.instagram_auth_url;
    } catch (error) {
      console.error("Error connecting Instagram:", error);
      toast.error("Failed to connect Instagram", {
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
          Click the button below to securely connect your Instagram account. You&apos;ll be redirected to Instagram to authorize the connection.
        </p>
        
        <div className="flex flex-col items-center gap-2">
          <Button
            type="button"
            className="w-full text-base font-semibold bg-white text-[#E4405F] border border-[#E4405F] hover:bg-[#fdf2f4] hover:text-[#C13584] p-2 shadow-md max-w-32"
            style={{ boxShadow: '0 2px 8px 0 rgba(228,64,95,0.10)', height: 'max-content' }}
            onClick={handleInstagramConnect}
            disabled={isConnecting}
          >
            <InstagramIcon style={{width: 100, height: 100}} />
          </Button>
        </div>
      </div>
    </div>
  );
}
