type PageRoutesType = {
  title: string;
  items: PageRoutesItemType;
};

type PageRoutesItemType = {
  title: string;
  href: string;
  icon?: string;
  isComing?: boolean;
  isDataBadge?: string;
  isNew?: boolean;
  newTab?: boolean;
  items?: PageRoutesItemType;
}[];

export const page_routes: PageRoutesType[] = [
  {
    title: "Oversikt",
    items: [
      {
        title: "Dashbord",
        href: "/dashboard/default",
        icon: "Activity",
      },
      {
        title: "Leads & kontakter",
        href: "/dashboard/leads",
        icon: "NotebookTabs",
      },
      { 
        title: "Kalender", 
        href: "/dashboard/apps/calendar", 
        icon: "Calendar" 
      },
    ],
  },
  {
    title: "Kommunikasjon & trening",
    items: [
      {
        title: "Kanaler",
        href: "/dashboard/apps/chat",
        icon: "MessageSquare",
      },
      { 
        title: "Trening", 
        href: "/dashboard/apps/training", 
        icon: "Network" 
      },
    ],
  },
  {
    title: "Pages",
    items: [
      {
        title: "Innstillinger",
        href: "/dashboard/pages/innstillinger",
        icon: "Settings",
        items: [
          { 
            title: "Kontekst", 
            href: "/dashboard/pages/innstillinger" 
          },
          {
            title: "Integrasjoner",
            href: "/dashboard/pages/innstillinger/integrasjoner",
          },
          {
            title: "Leads og oppfølging",
            href: "/dashboard/pages/innstillinger/leads",
          },
          { 
            title: "Konto", 
            href: "/dashboard/pages/innstillinger/konto" 
          },
        ],
      },
      // {
      //   title: "Pricing",
      //   href: "/dashboard/pages/pricing",
      //   icon: "BadgeDollarSign",
      // },
    ],
  },
];
