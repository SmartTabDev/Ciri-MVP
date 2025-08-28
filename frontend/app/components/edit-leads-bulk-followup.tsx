"use client";
import React, { useEffect, useState } from "react";
import { type DateValue, parseDate } from "@internationalized/date";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "./ui/form";
import { useForm } from "react-hook-form";
import { leadsSchema } from "@/schema/leads";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "./ui/button";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select";
import { useMotherStore } from "@/stores/motherStore";
import { DateInput } from "@heroui/react";

export default function EditLeadsFollowUp() {
  const { category, setName, setEmail, setFollowUp } = useMotherStore();
  const [intervalFrequency, setIntervalFrequency] = useState<string>("every");
  const [intervalDuration, setIntervalDuration] = useState<string>("month");
  const [intervalStart, setIntervalStart] = useState<DateValue | null>();

  const form = useForm<z.infer<typeof leadsSchema>>({
    resolver: zodResolver(leadsSchema),
    defaultValues: {
      followUp: {
        intervalDuration: "",
        intervalFrequency: "",
        intervalStart: new Date(),
      },
    },
  });

  useEffect(() => {
    console.log("here", intervalFrequency, intervalDuration, intervalStart);
  }, [intervalFrequency, intervalDuration, intervalStart]);

  const onSubmit = (vals: z.infer<typeof leadsSchema>) => {
    console.log("Submitted: ", {
      name: vals.name,
      email: vals.email,
      kategori: category,
      followUp: {
        intervalFrequency: intervalFrequency,
        intervalDuration: intervalDuration,
        intervalStart: intervalStart,
      },
    });

    setName(vals.name);
    setEmail(vals.email);
    setFollowUp({
      intervalDuration: vals.followUp.intervalDuration,
      intervalFrequency: vals.followUp.intervalFrequency,
      intervalStart: vals.followUp.intervalStart,
    });
  };

  return (
    <Form {...form}>
      <form
        className="flex flex-col items-center gap-4"
        onSubmit={form.handleSubmit(onSubmit)}
      >
        <FormField
          control={form.control}
          name="followUp"
          render={() => (
            <FormItem className="w-full">
              {/* <FormLabel>Oppfølginsintervall</FormLabel> */}
              <FormControl>
                <div className="flex flex-wrap items-center gap-2 text-nowrap">
                  <span>Følg opp</span>
                  <Select onValueChange={setIntervalFrequency}>
                    <SelectTrigger className="w-fit">
                      <SelectValue placeholder="hver" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="every">hver</SelectItem>
                      <SelectItem value="every-other">annenhver</SelectItem>
                      <SelectItem value="every-3rd">hver tredje</SelectItem>
                    </SelectContent>
                  </Select>

                  <Select onValueChange={setIntervalDuration}>
                    <SelectTrigger className="w-fit">
                      <SelectValue placeholder="måned" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="year">år</SelectItem>
                      <SelectItem value="month">måned</SelectItem>
                      <SelectItem value="week">uke</SelectItem>
                    </SelectContent>
                  </Select>
                  <div className="flex items-center gap-2">
                    <span>f.om</span>
                    <DateInput
                      onChange={setIntervalStart}
                      classNames={{
                        segment: "focus:bg-gray-700/30 focus:text-white ",
                      }}
                    />
                  </div>
                </div>
              </FormControl>
            </FormItem>
          )}
        ></FormField>

        <Button type="submit" variant="outline" className="w-full">
          Lagre
        </Button>
      </form>
    </Form>
  );
}
