# Shadcn UI Kit

This is a [Next.js 15](https://nextjs.org/) project bootstrapped with [create-next-app](https://github.com/vercel/next.js/tree/canary/packages/create-next-app) and React 19.

## Getting Started

Follow these steps to get your project up and running locally:

1. Clone the repository:

    ```sh
    git clone https://github.com/bundui/shadcn-ui-kit-dashboard.git
    cd shadcn-ui-kit-dashboard
    ```

2. Install dependencies: 

    ```sh
    npm install
    # or
    yarn install
    # or
    pnpm install
    ```

   If you encounter any problems installing packages, try adding the `--legacy-peer-deps` or `--force` flag:

    ```sh
    npm install --legacy-peer-deps
    ```

    Our recommendation is to use --legacy-peer-deps. [Examine this in more detail](https://ui.shadcn.com/docs/react-19).


1. Set up your environment variables:

   If your project includes an `.env.example` file, make sure to rename it to `.env` and fill in any necessary details.

    ```sh
    cp .env.example .env
    ```

2. Run the development server:

    ```sh
    npm run dev
    # or
    yarn dev
    # or
    pnpm dev
    ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser to view the result.

4. You can start editing the page by modifying `app/page.tsx`. The page will automatically update as you make changes.

