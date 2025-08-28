import React from "react";
import { UseFormReturn } from "react-hook-form";
import { Form, FormField, FormItem, FormControl, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface OnboardingCompanyFormProps {
  form: UseFormReturn<any>;
}

export const OnboardingCompanyForm: React.FC<OnboardingCompanyFormProps> = ({ form }) => (
  <Form {...form}>
    <div className="grid gap-6">
      <FormField
        control={form.control}
        name="companyName"
        render={({ field }) => (
          <FormItem>
            <Label htmlFor="companyName">Company Name</Label>
            <FormControl>
              <Input id="companyName" type="text" placeholder="Enter company name" className="rounded-[5px]!" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="businessEmail"
        render={({ field }) => (
          <FormItem>
            <Label htmlFor="businessEmail">Business Email</Label>
            <FormControl>
              <Input id="businessEmail" type="email" placeholder="Enter business email" className="rounded-[5px]!" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="businessCategory"
        render={({ field }) => (
          <FormItem>
            <Label htmlFor="businessCategory">Business Category</Label>
            <FormControl>
              <Input id="businessCategory" type="text" placeholder="Enter business category" className="rounded-[5px]!" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="phoneNumbers"
        render={({ field }) => (
          <FormItem>
            <Label htmlFor="phoneNumbers">Phone Numbers</Label>
            <FormControl>
              <Input id="phoneNumbers" type="text" placeholder="Enter phone numbers" className="rounded-[5px]!" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="goal"
        render={({ field }) => (
          <FormItem>
            <Label htmlFor="goal">Goal</Label>
            <FormControl>
              <Input id="goal" type="text" placeholder="Enter goal" className="rounded-[5px]!" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
      <FormField
        control={form.control}
        name="followUpCycle"
        render={({ field }) => (
          <FormItem>
            <Label htmlFor="followUpCycle">Follow Up Cycle</Label>
            <FormControl>
              <Input id="followUpCycle" type="text" placeholder="Enter follow up cycle" className="rounded-[5px]!" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  </Form>
); 