"use client";

import { GalleryVerticalEnd } from "lucide-react";
import { useState, useEffect } from "react";
import { Stepper } from "@/components/ui/stepper";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { OnboardingCompanyForm } from "@/components/auth/onboarding-company-form";
import { OnboardingCalendarForm } from "@/components/auth/onboarding-calendar-form";
import { OnboardingGmailForm } from "@/components/auth/onboarding-gmail-form";
import { OnboardingOutlookForm } from "@/components/auth/onboarding-outlook-form";
import { OnboardingInstagramForm } from "@/components/auth/onboarding-instagram-form";
import { OnboardingFacebookForm } from "@/components/auth/onboarding-facebook-form";
import { OnboardingTermsForm } from "@/components/auth/onboarding-terms-form";
import { Button } from "@/components/ui/button";
import { useSearchParams } from "next/navigation";
import axios from "axios";
import { getApiUrl } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { isEmpty } from "lodash";

const steps = [
  "Company Info",
  "Connect Calendar",
  "Connect Gmail",
  "Connect Outlook",
  "Connect Instagram",
  "Connect Facebook",
  "Terms of service",
];

const companyFormSchema = z.object({
  companyName: z.string().min(2, "Company name is required"),
  followUpCycle: z.string().min(1, "Follow up cycle is required"),
  businessEmail: z.string().email("Please enter a valid business email"),
  businessCategory: z.string().min(1, "Business category is required"),
  phoneNumbers: z.string().min(1, "Phone number is required"),
  goal: z.string().min(1, "Goal is required"),
});

type CompanyFormValues = z.infer<typeof companyFormSchema>;

const COMPANY_FORM_KEY = "onboarding_company_form";
const TERMS_KEY = "onboarding_terms";
const CALENDAR_TOKENS_KEY = "onboarding_calendar_tokens";
const GMAIL_TOKENS_KEY = "onboarding_gmail_tokens";
const GMAIL_EMAIL_KEY = "onboarding_gmail_email";
const GMAIL_USERNAME_KEY = "onboarding_gmail_username";
const OUTLOOK_TOKENS_KEY = "onboarding_outlook_tokens";
const OUTLOOK_EMAIL_KEY = "onboarding_outlook_email";
const OUTLOOK_USERNAME_KEY = "onboarding_outlook_username";
const INSTAGRAM_TOKENS_KEY = "onboarding_instagram_tokens";
const INSTAGRAM_USERNAME_KEY = "onboarding_instagram_username";
const INSTAGRAM_ACCOUNT_ID_KEY = "onboarding_instagram_account_id";
const FACEBOOK_TOKENS_KEY = "onboarding_facebook_tokens";
const FACEBOOK_PAGE_ID_KEY = "onboarding_facebook_page_id";
const FACEBOOK_PAGE_NAME_KEY = "onboarding_facebook_page_name";

export default function OnboardingPage() {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [terms, setTerms] = useState('');
  const [apiError, setApiError] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const router = useRouter();

  // Company form instance
  const companyForm = useForm<CompanyFormValues>({
    resolver: zodResolver(companyFormSchema),
    defaultValues: {
      companyName: "",
      followUpCycle: "",
      businessEmail: "",
      businessCategory: "",
      phoneNumbers: "",
      goal: "",
    },
    mode: "onChange",
  });

  // Persist calendar tokens to localStorage
  const setCompanyFormValues = (companyFormValues: any | null) => {
    if (typeof window !== "undefined") {
      if (companyFormValues) {
        localStorage.setItem(COMPANY_FORM_KEY, JSON.stringify(companyFormValues));
      } else {
        localStorage.removeItem(COMPANY_FORM_KEY);
      }
    }
  };

  // Persist calendar tokens to localStorage
  const setCalendarTokens = (tokens: { access_token: string; refresh_token: string } | null) => {
    if (typeof window !== "undefined") {
      if (tokens) {
        localStorage.setItem(CALENDAR_TOKENS_KEY, JSON.stringify(tokens));
      } else {
        localStorage.removeItem(CALENDAR_TOKENS_KEY);
      }
    }
  };

  // Persist gmail tokens to localStorage
  const setGmailBoxTokens = (tokens: { access_token: string; refresh_token: string } | null) => {
    if (typeof window !== "undefined") {
      if (tokens) {
        localStorage.setItem(GMAIL_TOKENS_KEY, JSON.stringify(tokens));
      } else {
        localStorage.removeItem(GMAIL_TOKENS_KEY);
      }
    }
  };

  // Persist outlook tokens to localStorage
  const setOutlookBoxTokens = (tokens: { access_token: string; refresh_token: string } | null) => {
    if (typeof window !== "undefined") {
      if (tokens) {
        localStorage.setItem(OUTLOOK_TOKENS_KEY, JSON.stringify(tokens));
      } else {
        localStorage.removeItem(OUTLOOK_TOKENS_KEY);
      }
    }
  };

  // Persist Instagram tokens to localStorage
  const setInstagramTokens = (tokens: { access_token: string; refresh_token: string } | null) => {
    if (typeof window !== "undefined") {
      if (tokens) {
        localStorage.setItem(INSTAGRAM_TOKENS_KEY, JSON.stringify(tokens));
      } else {
        localStorage.removeItem(INSTAGRAM_TOKENS_KEY);
      }
    }
  };

  // Persist Facebook tokens to localStorage
  const setFacebookTokens = (tokens: { access_token: string; refresh_token: string } | null) => {
    if (typeof window !== "undefined") {
      if (tokens) {
        localStorage.setItem(FACEBOOK_TOKENS_KEY, JSON.stringify(tokens));
      } else {
        localStorage.removeItem(FACEBOOK_TOKENS_KEY);
      }
    }
  };

  useEffect(() => {
    const access_token = searchParams.get("access_token");
    const refresh_token = searchParams.get("refresh_token");
    const onboarding_step = searchParams.get("onboarding_step");
    const gmail_email = searchParams.get("gmail_address");
    const gmail_username = searchParams.get("gmail_username");
    const outlook_email = searchParams.get("outlook_address");
    const outlook_username = searchParams.get("outlook_username");
    const instagram_username = searchParams.get("instagram_username");
    const instagram_account_id = searchParams.get("instagram_account_id");
    const facebook_page_id = searchParams.get("facebook_page_id");
    const facebook_page_name = searchParams.get("facebook_page_name");
    
    if (gmail_email) {
      if (typeof window !== "undefined") {
        localStorage.setItem(GMAIL_EMAIL_KEY, gmail_email);
      }
    }
    
    if (gmail_username) {
      if (typeof window !== "undefined") {
        localStorage.setItem(GMAIL_USERNAME_KEY, gmail_username);
      }
    }
    if (outlook_email) {
      if (typeof window !== "undefined") {
        localStorage.setItem(OUTLOOK_EMAIL_KEY, outlook_email);
      }
    }
    if (outlook_username) {
      if (typeof window !== "undefined") {
        localStorage.setItem(OUTLOOK_USERNAME_KEY, outlook_username);
      }
    }
    if (instagram_username) {
      if (typeof window !== "undefined") {
        localStorage.setItem(INSTAGRAM_USERNAME_KEY, instagram_username);
      }
    }
    if (instagram_account_id) {
      if (typeof window !== "undefined") {
        localStorage.setItem(INSTAGRAM_ACCOUNT_ID_KEY, instagram_account_id);
      }
    }
    if (facebook_page_id) {
      if (typeof window !== "undefined") {
        localStorage.setItem(FACEBOOK_PAGE_ID_KEY, facebook_page_id);
      }
    }
    if (facebook_page_name) {
      if (typeof window !== "undefined") {
        localStorage.setItem(FACEBOOK_PAGE_NAME_KEY, facebook_page_name);
      }
    }

    if (access_token) {
      if (onboarding_step === 'calendar') {
        setCurrentStep(2);
        setCalendarTokens({ access_token, refresh_token: refresh_token || '' });
      }
      if (onboarding_step === 'gmail-box') {
        setCurrentStep(3);
        setGmailBoxTokens({ access_token, refresh_token: refresh_token || '' });
      }
      if (onboarding_step === 'outlook-box') {
        setCurrentStep(4);
        setOutlookBoxTokens({ access_token, refresh_token: refresh_token || '' });
      }
      if (onboarding_step === 'instagram-box') {
        setCurrentStep(4);
        setInstagramTokens({ access_token, refresh_token: refresh_token || '' });
      }
      if (onboarding_step === 'facebook-box') {
        setCurrentStep(5);
        setFacebookTokens({ access_token, refresh_token: refresh_token || '' });
      }
    }
  }, [searchParams]);

  const handleCompanySubmit = (data: CompanyFormValues) => {
    setCompanyFormValues(data);
    setCurrentStep((s) => Math.min(steps.length - 1, s + 1));
  };

  const handleNext = () => {
    if (currentStep === 0) {
      setCompanyFormValues(companyForm.getValues());
    }
    setCurrentStep(prev => prev + 1);
  };

  // --- API call for company creation ---
  async function handleFinish() {
    setLoading(true);
    setApiError(null);
    try {
      const storedCompany: any = await JSON.parse(localStorage.getItem(COMPANY_FORM_KEY) ?? '{}');
      const storedCalendarTokens = await JSON.parse(localStorage.getItem(CALENDAR_TOKENS_KEY) ?? '{}');
      const storedGmailTokens = await JSON.parse(localStorage.getItem(GMAIL_TOKENS_KEY) ?? '{}');
      const storedGmailEmail = localStorage.getItem(GMAIL_EMAIL_KEY) ?? '';
      const storedGmailUsername = localStorage.getItem(GMAIL_USERNAME_KEY) ?? '';
      const storedGmailAppPassword = localStorage.getItem("onboarding_gmail_app_password") ?? '';
      const storedOutlookTokens = await JSON.parse(localStorage.getItem(OUTLOOK_TOKENS_KEY) ?? '{}');
      const storedOutlookEmail = localStorage.getItem(OUTLOOK_EMAIL_KEY) ?? '';
      const storedOutlookUsername = localStorage.getItem(OUTLOOK_USERNAME_KEY) ?? '';
      const storedInstagramTokens = await JSON.parse(localStorage.getItem(INSTAGRAM_TOKENS_KEY) ?? '{}');
      const storedInstagramUsername = localStorage.getItem(INSTAGRAM_USERNAME_KEY) ?? '';
      const storedInstagramAccountId = localStorage.getItem(INSTAGRAM_ACCOUNT_ID_KEY) ?? '';
      const storedFacebookTokens = await JSON.parse(localStorage.getItem(FACEBOOK_TOKENS_KEY) ?? '{}');
      const storedFacebookPageId = localStorage.getItem(FACEBOOK_PAGE_ID_KEY) ?? '';
      const storedFacebookPageName = localStorage.getItem(FACEBOOK_PAGE_NAME_KEY) ?? '';
      
      // Helper function to convert empty strings to undefined
      const emptyToUndefined = (value: string) => value === '' ? undefined : value;
      
      // Map form fields to backend API payload
      const payload = {
        name: storedCompany?.companyName,
        follow_up_cycle: Number(storedCompany?.followUpCycle),
        business_email: storedCompany?.businessEmail,
        business_category: storedCompany?.businessCategory,
        phone_numbers: storedCompany?.phoneNumbers,
        goal: storedCompany?.goal,
        terms_of_service: terms,
        gmail_box_credentials: isEmpty(storedGmailTokens) ? undefined : storedGmailTokens,
        calendar_credentials: isEmpty(storedCalendarTokens) ? undefined : storedCalendarTokens,
        gmail_box_email: emptyToUndefined(storedGmailEmail),
        gmail_box_username: emptyToUndefined(storedGmailUsername),
        gmail_box_app_password: emptyToUndefined(storedGmailAppPassword),
        outlook_box_credentials: isEmpty(storedOutlookTokens) ? undefined : storedOutlookTokens,
        outlook_box_email: emptyToUndefined(storedOutlookEmail),
        outlook_box_username: emptyToUndefined(storedOutlookUsername),
        instagram_credentials: isEmpty(storedInstagramTokens) ? undefined : storedInstagramTokens,
        instagram_username: emptyToUndefined(storedInstagramUsername),
        instagram_account_id: emptyToUndefined(storedInstagramAccountId),
        instagram_page_id: emptyToUndefined(storedInstagramAccountId), // For Instagram Basic Display API, account_id is used as page_id
        facebook_box_credentials: isEmpty(storedFacebookTokens) ? undefined : storedFacebookTokens,
        facebook_box_page_id: emptyToUndefined(storedFacebookPageId),
        facebook_box_page_name: emptyToUndefined(storedFacebookPageName),
      };
      await axios.post(getApiUrl() + "/v1/companies", payload, {
        headers: {
          "Content-Type": "application/json",
          ...(typeof window !== "undefined" && localStorage.getItem("access_token")
            ? { Authorization: `Bearer ${localStorage.getItem("access_token")}` }
            : {}),
        },
      });
      // Clear localStorage after successful submit
      if (typeof window !== "undefined") {
        localStorage.removeItem(COMPANY_FORM_KEY);
        localStorage.removeItem(TERMS_KEY);
        localStorage.removeItem(CALENDAR_TOKENS_KEY);
        localStorage.removeItem(GMAIL_TOKENS_KEY);
        localStorage.removeItem(GMAIL_EMAIL_KEY);
        localStorage.removeItem(GMAIL_USERNAME_KEY);
        localStorage.removeItem("onboarding_gmail_app_password");
        localStorage.removeItem(OUTLOOK_TOKENS_KEY);
        localStorage.removeItem(OUTLOOK_EMAIL_KEY);
        localStorage.removeItem(OUTLOOK_USERNAME_KEY);
        localStorage.removeItem(INSTAGRAM_TOKENS_KEY);
        localStorage.removeItem(INSTAGRAM_USERNAME_KEY);
        localStorage.removeItem(INSTAGRAM_ACCOUNT_ID_KEY);
        localStorage.removeItem(FACEBOOK_TOKENS_KEY);
        localStorage.removeItem(FACEBOOK_PAGE_ID_KEY);
        localStorage.removeItem(FACEBOOK_PAGE_NAME_KEY);
      }
      router.replace("/dashboard");
    } catch (err: any) {
      setApiError(
        err.response?.data?.detail || err.message || "Failed to create company"
      );
    } finally {
      setLoading(false);
    }
  }

  // Step configuration array
  const stepConfigs = [
    {
      key: "company",
      render: () => (
        <OnboardingCompanyForm form={companyForm} />
      ),
      isForm: true,
      onSubmit: companyForm.handleSubmit(handleCompanySubmit),
    },
    {
      key: "calendar",
      render: () => <OnboardingCalendarForm />,
      isForm: false,
    },
    {
      key: "gmail",
      render: () => <OnboardingGmailForm />,
      isForm: false,
    },
    {
      key: "outlook",
      render: () => <OnboardingOutlookForm />,
      isForm: false,
    },
    {
      key: "instagram",
      render: () => <OnboardingInstagramForm />,
      isForm: false,
    },
    {
      key: "facebook",
      render: () => <OnboardingFacebookForm />,
      isForm: false,
    },
    {
      key: "terms",
      render: () => <OnboardingTermsForm terms={terms} setTerms={setTerms} />,
      isForm: false,
    },
  ];

  // Render step content
  function renderStep() {
    const config = stepConfigs[currentStep];
    if (!config) return null;
    if (config.isForm) {
      return (
        <form className="w-full" onSubmit={config.onSubmit}>
          {config.render()}
          {renderNavButtons(true)}
        </form>
      );
    }
    return (
      <>
        {config.render()}
        {renderNavButtons(false)}
      </>
    );
  }

  // Render navigation buttons
  function renderNavButtons(isFormStep: boolean) {
    const isLastStep = currentStep === steps.length - 1;
    const showSkip = currentStep === 1 || currentStep === 2 || currentStep === 3 || currentStep === 4 || currentStep === 5; // Calendar, Gmail, Outlook, Instagram, Facebook steps
    const showNext = !showSkip && !isLastStep;
    return (
      <div className="flex gap-2 w-full justify-between mt-8">
        <Button
          variant="outline"
          className=""
          onClick={() => setCurrentStep((s) => Math.max(0, s - 1))}
          disabled={currentStep === 0 || loading}
          type="button"
        >
          Previous
        </Button>
        <div className="flex gap-2 ml-auto">
          {showSkip && (
            <Button
              variant="ghost"
              className=""
              type="button"
              onClick={() => setCurrentStep((s) => s + 1)}
              disabled={loading}
            >
              Skip
            </Button>
          )}
          {isLastStep ? (
            <Button
              className=""
              type="button"
              onClick={handleFinish}
              disabled={!terms.trim() || loading}
            >
              {loading ? "Submitting..." : "Finish"}
            </Button>
          ) : (
            showNext && (
              <Button
                className=""
                type={isFormStep ? "submit" : "button"}
                // Only add onClick for non-form steps
                {...(!isFormStep ? { onClick: handleNext } : {})}
                disabled={currentStep === steps.length - 1 || loading}
              >
                Next
              </Button>
            )
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-background grid min-h-svh lg:grid-cols-2">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <a href="#" className="flex items-center gap-2 font-medium">
            <div className="bg-primary text-primary-foreground flex size-6 items-center justify-center rounded-md">
              <GalleryVerticalEnd className="size-4" />
            </div>
            Acme Inc.
          </a>
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="w-full max-w-sm">
            <Stepper steps={steps} currentStep={currentStep} />
            <div className="flex flex-col gap-6 items-center mt-8">
              <h1 className="font-display text-2xl text-center">{steps[currentStep]}</h1>
              {apiError && <div className="text-destructive text-sm mb-2">{apiError}</div>}
              {renderStep()}
            </div>
          </div>
        </div>
      </div>
      <div className="bg-muted relative hidden lg:block">
        <img
          src="/bakgrunnn.png"
          alt="Image"
          className="absolute inset-0 h-full w-full object-cover dark:brightness-[0.2] dark:grayscale"
        />
      </div>
    </div>
  );
} 