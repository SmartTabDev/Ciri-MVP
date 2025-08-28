"use client";

import * as React from "react";
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { ArrowDownIcon, ArrowUpIcon, ChevronDown } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { ExportButton } from "@/components/CardActionMenus";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import ChatHistory from "@/components/ChatHistory";
import { format } from "date-fns";
import Icon from "@/components/icon-component";
import { LeadsUpload } from "./leads-upload";
import { Checkbox } from "./ui/checkbox";
import EditLeads from "./edit-leads";
import { EditLeadsBulk } from "./edit-bulk-leads";

type Order = {
  id: string;
  navn: string;
  email: string;
  threadData: {
    threadFrom: {
      message: string;
      date: Date;
    };
    threadTo: {
      message: string;
      date: Date;
    };
  }[];
  followUp: Date;
  items: number;
  amount: number;
  paymentMethod: string;
  kategori: "feelgood" | "gjenkjøp";
  status: "fullført" | "pågår" | "venter" | "tapt";
};

const data: Order[] = [
  {
    id: "1083",
    navn: "Fredrik",
    email: "fredrik@nord.no",
    threadData: [
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
    ],
    items: 2,
    followUp: new Date("2025,06,20, 09:00:00"),
    kategori: "feelgood",
    amount: 34.5,
    paymentMethod: "E-Wallet",
    status: "venter",
  },
  {
    id: "1082",
    navn: "Maren",
    email: "maren@nord.no",
    threadData: [
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
    ],
    followUp: new Date("2025,06,22, 14:00:00"),
    kategori: "feelgood",
    items: 6,
    amount: 60.5,
    paymentMethod: "Bank Transfer",
    status: "fullført",
  },
  {
    id: "1081",
    navn: "Samuel",
    email: "samuel@nord.no",
    threadData: [
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
    ],
    followUp: new Date("2025,06,30, 15:00:00"),
    kategori: "gjenkjøp",
    items: 3,
    amount: 47.5,
    paymentMethod: "E-Wallet",
    status: "fullført",
  },
  {
    id: "1079",
    navn: "Rolf",
    email: "rolf@nord.no",
    threadData: [
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
      {
        threadFrom: {
          message:
            "Hei Fredrik! Jeg ser du bestilte time hos oss for ett år siden, og lurte på om du kanskje ville komme tilbake og prøve deg på en ny? ✨",
          date: new Date("2025.06.10, 18:00:01"),
        },
        threadTo: {
          message:
            "Takk for oppfølging! Ja, jeg har faktisk tenkt på om jeg skulle bestille en ny time, men har ikke kommet så langt enda. Jeg tar gjerne en prat 😊",
          date: new Date("2025.06.12, 18:00:01"),
        },
      },
    ],
    followUp: new Date("2025,07,01, 10:00:00"),
    kategori: "gjenkjøp",
    items: 15,
    amount: 89.8,
    paymentMethod: "Bank Transfer",
    status: "pågår",
  },
];

const columns: ColumnDef<Order>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "navn",
    header: "Navn",
  },
  {
    accessorKey: "email",
    header: "E-post",
    cell: ({ row }) => `${row.getValue("email")}`,
  },
  {
    accessorKey: "followUp",
    header: "Oppfølging",
    cell: ({ row }) =>
      `${format(row.getValue("followUp"), "d. MMM yyyy 'kl.' HH:mm")}`,
  },
  {
    accessorKey: "kategori",
    header: "Kategori",
    cell: ({ row }) => {
      const { kategori } = row.original;

      const categoryMap = {
        feelgood: "feelgood",
        gjenkjøp: "gjenkjøp",
      } as const;

      const iconsMap = {
        feelgood: "HandHeart",
        gjenkjøp: "HandCoins",
      } as const;

      const categoryClass = categoryMap[kategori] ?? "default";

      const iconsClass = iconsMap[kategori];

      return (
        <Badge
          variant={categoryClass}
          className="flex items-center gap-1 capitalize"
        >
          <Icon name={iconsClass} />
          {kategori.replace("-", " ")}
        </Badge>
      );
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status;

      const statusMap = {
        fullført: "success",
        pågår: "info",
        venter: "warning",
        tapt: "destructive",
      } as const;

      const statusClass = statusMap[status] ?? "default";

      return (
        <Badge variant={statusClass} className="capitalize">
          {status.replace("-", " ")}
        </Badge>
      );
    },
  },

  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const { navn, threadData } = row.original;

      return (
        <Dialog>
          <DialogTrigger className="hover:cursor-pointer hover:opacity-80">
            Se samtalen
          </DialogTrigger>
          <DialogContent className="max-h-10/12">
            <DialogTitle>Historikken til {navn}</DialogTitle>
            <DialogDescription>
              <ChatHistory leadName={navn} threadData={threadData} />
            </DialogDescription>
          </DialogContent>
        </Dialog>
      );
    },
  },

  {
    id: "edit",
    cell: ({ row }) => {
      const { kategori, navn, status, email } = row.original;

      const statusMap = {
        fullført: "success",
        pågår: "info",
        venter: "warning",
        tapt: "destructive",
      } as const;

      const statusClass = statusMap[status] ?? "default";

      return (
        <Dialog>
          <DialogTrigger className="hover:cursor-pointer hover:opacity-80">
            Endre
          </DialogTrigger>
          <DialogContent className="max-h-10/12 w-fit!">
            <DialogTitle>Endre data for {navn}</DialogTitle>
            <DialogDescription>
              <EditLeads kategori={kategori} name={navn} email={email} />
            </DialogDescription>
          </DialogContent>
        </Dialog>
      );
    },
  },
];

//todo add some other cool graphs to the leads section

export function TableOrderStatus({ dashboard }: { dashboard?: boolean }) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    [],
  );
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});
  const [complete, setComplete] = React.useState<number>();
  const [progress, setProgress] = React.useState<number>();
  const [awaiting, setAwaiting] = React.useState<number>();
  const [lost, setLost] = React.useState<number>();
  const [totalCount, setTotalCount] = React.useState<number>();
  const [completePercent, setCompletePercent] = React.useState<number>(0);
  const [progressPercent, setProgressPercent] = React.useState<number>(0);
  const [awaitingPercent, setAwaitingPercent] = React.useState<number>(0);
  const [lostPercent, setLostPercent] = React.useState<number>(0);

  const table = useReactTable({
    data,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
    initialState: {
      pagination: {
        pageSize: 6,
      },
    },
  });

  const selectedRowsCount = Object.keys(rowSelection).length;

  const selectedRows = table.getSelectedRowModel().rows;

  const selectedLeads: string[] = selectedRows.map(({ original }) => {
    const { id } = original;
    return id;
  });

  React.useMemo(() => {
    const completeCount = data.filter((v, i) => v.status === "fullført").length;
    const inProgressCount = data.filter((v, i) => v.status === "pågår").length;
    const awaitingCount = data.filter((v, i) => v.status === "venter").length;
    const lostCount = data.filter((v, i) => v.status === "tapt").length;

    console.log(
      "Values: ",
      completeCount,
      inProgressCount,
      awaitingCount,
      lostCount,
    );

    const test = 1;

    setComplete(completeCount);
    setProgress(inProgressCount);
    setAwaiting(awaitingCount);
    setLost(lostCount);
  }, []);

  React.useMemo(() => {
    if (
      complete === undefined ||
      progress === undefined ||
      awaiting === undefined ||
      lost === undefined
    ) {
      setTotalCount(0);
      setCompletePercent(0);
      setProgressPercent(0);
      setAwaitingPercent(0);
      setLostPercent(0);
      return;
    } else {
      const total = complete + progress + awaiting + lost;
      setTotalCount(total);

      setCompletePercent(total > 0 ? (complete / total) * 100 : 0);
      setProgressPercent(total > 0 ? (progress / total) * 100 : 0);
      setAwaitingPercent(total > 0 ? (awaiting / total) * 100 : 0);
      setLostPercent(total > 0 ? (lost / total) * 100 : 0);
    }
  }, [complete, progress, awaiting, lost]);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Leads og kundeoversikt</CardTitle>
        <CardDescription>
          Full oversikt over alle kundehenvendelser i alle kanaler
        </CardDescription>
        <CardAction>
          <ExportButton />
        </CardAction>
      </CardHeader>
      <CardContent>
        <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-2">
            <div className="font-display text-2xl lg:text-3xl">{complete}</div>
            <div className="flex gap-2">
              <div className="text-muted-foreground text-sm">Fullført</div>
              <div className="flex items-center gap-0.5 text-xs text-green-500">
                <ArrowUpIcon className="size-3" />
                0.5%
              </div>
            </div>
            <Progress
              value={completePercent}
              className="h-2 bg-green-100 dark:bg-green-950"
              indicatorColor="bg-green-400"
            />
          </div>
          <div className="space-y-2">
            <div className="font-display text-2xl lg:text-3xl">{progress}</div>
            <div className="flex gap-2">
              <div className="text-muted-foreground text-sm">Pågår</div>
              <div className="flex items-center gap-0.5 text-xs text-red-500">
                <ArrowDownIcon className="size-3" />
                0.3%
              </div>
            </div>
            <Progress
              value={progressPercent}
              className="h-2 bg-blue-100 dark:bg-blue-950"
              indicatorColor="bg-blue-400"
            />
          </div>
          <div className="space-y-2">
            <div className="font-display text-2xl lg:text-3xl">{awaiting}</div>
            <div className="flex gap-2">
              <div className="text-muted-foreground text-sm">Venter</div>
              <div className="flex items-center gap-0.5 text-xs text-green-500">
                <ArrowUpIcon className="size-3" />
                0.5%
              </div>
            </div>
            <Progress
              value={awaitingPercent}
              className="h-2 bg-gray-100 dark:bg-gray-950"
              indicatorColor="bg-gray-400"
            />
          </div>
          <div className="space-y-2">
            <div className="font-display text-2xl lg:text-3xl">{lost}</div>
            <div className="flex gap-2">
              <div className="text-muted-foreground text-sm">Tapt</div>
              <div className="flex items-center gap-0.5 text-xs text-red-500">
                <ArrowDownIcon className="size-3" />
                0.5%
              </div>
            </div>
            <Progress
              value={lostPercent}
              className="h-2 bg-red-100 dark:bg-red-950"
              indicatorColor="bg-red-400"
            />
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <Input
              placeholder="Filter orders..."
              value={
                (table.getColumn("navn")?.getFilterValue() as string) ?? ""
              }
              onChange={(event) =>
                table.getColumn("navn")?.setFilterValue(event.target.value)
              }
              className="max-w-sm"
            />
            {selectedRowsCount > 0 && (
              <EditLeadsBulk
                id={selectedLeads}
                countSelected={selectedRowsCount}
              />
            )}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="ml-auto">
                  Kolonner <ChevronDown />
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end">
                {table
                  .getAllColumns()
                  .filter((column) => column.getCanHide())
                  .map((column) => {
                    return (
                      <DropdownMenuCheckboxItem
                        key={column.id}
                        className="capitalize"
                        checked={column.getIsVisible()}
                        onCheckedChange={(value) =>
                          column.toggleVisibility(!!value)
                        }
                      >
                        {column.id}
                      </DropdownMenuCheckboxItem>
                    );
                  })}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                {table.getHeaderGroups().map((headerGroup) => (
                  <TableRow key={headerGroup.id}>
                    {headerGroup.headers.map((header) => {
                      return (
                        <TableHead key={header.id}>
                          {header.isPlaceholder
                            ? null
                            : flexRender(
                                header.column.columnDef.header,
                                header.getContext(),
                              )}
                        </TableHead>
                      );
                    })}
                  </TableRow>
                ))}
              </TableHeader>
              <TableBody>
                {table.getRowModel().rows?.length ? (
                  table.getRowModel().rows.map((row) => (
                    <TableRow
                      key={row.id}
                      data-state={row.getIsSelected() && "selected"}
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id}>
                          {flexRender(
                            cell.column.columnDef.cell,
                            cell.getContext(),
                          )}
                        </TableCell>
                      ))}
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell
                      colSpan={columns.length}
                      className="h-24 text-center"
                    >
                      No results.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
          <div className="flex items-center justify-end space-x-2">
            <div className="text-muted-foreground flex-1 text-sm">
              {table.getFilteredSelectedRowModel().rows.length} of{" "}
              {table.getFilteredRowModel().rows.length} row(s) selected.
            </div>
            <div className="space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
