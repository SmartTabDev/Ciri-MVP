import { betterAuth } from "better-auth";
import { createAuthClient } from "better-auth/react";

export const auth = betterAuth({
  socialProviders: {
    google: {
      clientId: "",
      clientSecret: "",
      scope: [""],
    },
  },
});

export const authClient = createAuthClient({});
