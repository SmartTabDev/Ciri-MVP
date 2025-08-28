import type { NextConfig } from "next";

import { config } from "dotenv";

config();

const isProduction = process.env.NODE_ENV === "production";

const nextConfig: NextConfig = {
  assetPrefix: isProduction ? process.env.DASHBOARD_BASE_URL : undefined,
  env: {
    // To use environment variables in the project without using the "NEXT_PUBLIC_" prefix
    BASE_URL: process.env.BASE_URL,
    DASHBOARD_BASE_URL: process.env.DASHBOARD_BASE_URL,
    ASSETS_URL: process.env.ASSETS_URL,
    GA_KEY: process.env.GA_KEY,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL
  },
  async headers() {
    return [
      {
        // Apply these headers to all routes
        source: '/(.*)',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization, X-Refresh-Token',
          },
        ],
      },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost"
      },
      {
        protocol: "https",
        hostname: "dashboard.shadcnuikit.com"
      },
      {
        protocol: "https",
        hostname: "bundui-images.netlify.app"
      }
    ]
  }
};

export default nextConfig;
