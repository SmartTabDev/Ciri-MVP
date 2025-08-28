"use client";

import Link from "next/link";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Icons } from "@/components";
import { Input } from "@/components/ui/input";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Switch } from "@/components/ui/switch";
import { toast } from "@/components/ui/use-toast";
import { Card, CardContent } from "@/components/ui/card";
import { useUser } from "@/contexts/user-context";
import { companyService, CompanyData } from "@/services/company-service";
import { getApiUrl } from "@/lib/utils";

const notificationsFormSchema = z.object({
  mobile: z.boolean().default(false).optional(),
  google_calendar: z.boolean().default(false).optional(),
  google_email: z.boolean().default(false).optional(),
  outlook_email: z.boolean().default(false).optional(),
  instagram: z.boolean().default(false).optional(),
  facebook: z.boolean().default(false).optional(),
});

type NotificationsFormValues = z.infer<typeof notificationsFormSchema>;

export default function Page() {
  const { user } = useUser();
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isConnecting, setIsConnecting] = useState<string | null>(null);
  const [gmailAppPassword, setGmailAppPassword] = useState("");

  // Check integration status based on stored credentials
  const getIntegrationStatus = () => {
    if (!companyData) return {
      google_calendar: false,
      google_email: false,
      outlook_email: false,
      instagram: false,
      facebook: false,
    };

    return {
      google_calendar: !!(companyData.calendar_credentials),
      google_email: !!(companyData.gmail_box_credentials || companyData.gmail_box_email),
      outlook_email: !!(companyData.outlook_box_credentials || companyData.outlook_box_email),
      instagram: !!(companyData.instagram_credentials || companyData.instagram_username),
      facebook: !!(companyData.facebook_box_credentials || companyData.facebook_box_page_id),
    };
  };

  const integrationStatus = getIntegrationStatus();

  const form = useForm<NotificationsFormValues>({
    resolver: zodResolver(notificationsFormSchema),
    defaultValues: integrationStatus,
  });

  // Load company data when component mounts
  useEffect(() => {
    const loadCompanyData = async () => {
      if (!user?.company_id) return;
      
      setIsLoading(true);
      try {
        const data = await companyService.getCompany(user.company_id);
        setCompanyData(data);
      } catch (error) {
        console.error("Error loading company data:", error);
        toast({
          title: "Error",
          description: "Kunne ikke laste integrasjonsdata",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadCompanyData();
  }, [user?.company_id]);

  // Handle OAuth callbacks
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const onboardingStep = urlParams.get('onboarding_step');
    
    if (onboardingStep) {
      // Clear the URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
      
      // Handle credential storage based on the integration
      const handleCredentialStorage = async () => {
        if (!user?.company_id) return;
        
        try {
          const updateData: any = {};
          
          switch (onboardingStep) {
            case 'calendar':
              // Store calendar credentials
              const accessToken = urlParams.get('access_token');
              const refreshToken = urlParams.get('refresh_token');
              if (accessToken && refreshToken) {
                updateData.calendar_credentials = {
                  access_token: accessToken,
                  refresh_token: refreshToken,
                  token_type: 'Bearer',
                  expires_in: 3600
                };
              }
              break;
              
            case 'gmail-box':
              // Store Gmail credentials
              const gmailAccessToken = urlParams.get('access_token');
              const gmailRefreshToken = urlParams.get('refresh_token');
              const gmailAddress = urlParams.get('gmail_address');
              const gmailUsername = urlParams.get('gmail_username');
              const gmailAppPassword = localStorage.getItem("onboarding_gmail_app_password");
              
              if (gmailAccessToken && gmailRefreshToken) {
                updateData.gmail_box_credentials = {
                  access_token: gmailAccessToken,
                  refresh_token: gmailRefreshToken,
                  token_type: 'Bearer',
                  expires_in: 3600
                };
                updateData.gmail_box_email = gmailAddress;
                updateData.gmail_box_username = gmailUsername;
                updateData.gmail_box_app_password = gmailAppPassword;
                
                // Clear the app password from localStorage
                localStorage.removeItem("onboarding_gmail_app_password");
              }
              break;
              
            case 'outlook-box':
              // Store Outlook credentials
              const outlookAccessToken = urlParams.get('access_token');
              const outlookRefreshToken = urlParams.get('refresh_token');
              const outlookAddress = urlParams.get('outlook_address');
              const outlookUsername = urlParams.get('outlook_username');
              
              if (outlookAccessToken && outlookRefreshToken) {
                updateData.outlook_box_credentials = {
                  access_token: outlookAccessToken,
                  refresh_token: outlookRefreshToken,
                  token_type: 'Bearer',
                  expires_in: 3600
                };
                updateData.outlook_box_email = outlookAddress;
                updateData.outlook_box_username = outlookUsername;
              }
              break;

            case 'instagram':
              // Store Instagram credentials
              const instagramAccessToken = urlParams.get('access_token');
              const instagramRefreshToken = urlParams.get('refresh_token');
              const instagramUsername = urlParams.get('instagram_username');
              const instagramAccountId = urlParams.get('instagram_account_id');
              const instagramPageId = urlParams.get('instagram_page_id');
              
              if (instagramAccessToken && instagramRefreshToken) {
                updateData.instagram_credentials = {
                  access_token: instagramAccessToken,
                  refresh_token: instagramRefreshToken,
                  token_type: 'Bearer',
                  expires_in: 3600
                };
                updateData.instagram_username = instagramUsername;
                updateData.instagram_account_id = instagramAccountId;
                updateData.instagram_page_id = instagramPageId;
              }
              break;

            case 'facebook':
              // Store Facebook credentials
              const facebookAccessToken = urlParams.get('access_token');
              const facebookRefreshToken = urlParams.get('refresh_token');
              const facebookPageId = urlParams.get('facebook_page_id');
              const facebookPageName = urlParams.get('facebook_page_name');
              
              if (facebookAccessToken && facebookRefreshToken) {
                updateData.facebook_box_credentials = {
                  access_token: facebookAccessToken,
                  refresh_token: facebookRefreshToken,
                  token_type: 'Bearer',
                  expires_in: 3600
                };
                updateData.facebook_box_page_id = facebookPageId;
                updateData.facebook_box_page_name = facebookPageName;
              }
              break;
          }
          
          // Update company with credentials
          if (Object.keys(updateData).length > 0) {
            await companyService.updateCompany(user.company_id, updateData);
            
            // Reload company data
            const data = await companyService.getCompany(user.company_id);
            setCompanyData(data);
          }
          
          // Show success message
          let integrationName = '';
          switch (onboardingStep) {
            case 'calendar':
              integrationName = 'Google Calendar';
              break;
            case 'gmail-box':
              integrationName = 'Gmail';
              break;
            case 'outlook-box':
              integrationName = 'Outlook';
              break;
            case 'instagram':
              integrationName = 'Instagram';
              break;
            case 'facebook':
              integrationName = 'Facebook';
              break;
          }
          
          if (integrationName) {
            toast({
              title: "Success",
              description: `${integrationName} koblet til!`,
            });
          }
          
        } catch (error) {
          console.error("Error storing credentials:", error);
          toast({
            title: "Error",
            description: "Kunne ikke lagre integrasjonsdata",
            variant: "destructive",
          });
        }
      };
      
      handleCredentialStorage();
    }
  }, [user?.company_id]);

  // Update form when company data changes
  useEffect(() => {
    if (companyData) {
      const status = getIntegrationStatus();
      form.reset(status);
    }
  }, [companyData, form]);

  // Handle integration connections
  const handleConnect = (integration: string) => {
    setIsConnecting(integration);
    
    switch (integration) {
      case 'google_calendar':
        window.location.href = getApiUrl() + "/v1/auth/calendar/login?redirect_to=settings";
        break;
      case 'google_email':
        // Store app password in localStorage before redirecting
        if (gmailAppPassword) {
          localStorage.setItem("onboarding_gmail_app_password", gmailAppPassword);
        }
        window.location.href = getApiUrl() + "/v1/auth/gmail/login?redirect_to=settings";
        break;
      case 'outlook_email':
        window.location.href = getApiUrl() + "/v1/auth/outlook/login?redirect_to=settings";
        break;
      case 'instagram':
        window.location.href = getApiUrl() + "/v1/instagram/auth-url";
        break;
      case 'facebook':
        window.location.href = getApiUrl() + "/v1/facebook/auth-url";
        break;
      default:
        setIsConnecting(null);
    }
  };

  // Handle integration disconnections
  const handleDisconnect = async (integration: string) => {
    if (!user?.company_id) return;

    setIsConnecting(integration);
    
    try {
      const updateData: any = {};
      
      switch (integration) {
        case 'google_calendar':
          updateData.calendar_credentials = null;
          break;
        case 'google_email':
          updateData.gmail_box_credentials = null;
          updateData.gmail_box_email = null;
          updateData.gmail_box_username = null;
          break;
        case 'outlook_email':
          updateData.outlook_box_credentials = null;
          updateData.outlook_box_email = null;
          updateData.outlook_box_username = null;
          break;
        case 'instagram':
          updateData.instagram_credentials = null;
          updateData.instagram_username = null;
          updateData.instagram_account_id = null;
          updateData.instagram_page_id = null;
          break;
        case 'facebook':
          updateData.facebook_box_credentials = null;
          updateData.facebook_box_page_id = null;
          updateData.facebook_box_page_name = null;
          break;
      }

      await companyService.updateCompany(user.company_id, updateData);
      
      // Reload company data
      const data = await companyService.getCompany(user.company_id);
      setCompanyData(data);
      
      toast({
        title: "Success",
        description: `${integration.replace('_', ' ')} koblet fra`,
      });
    } catch (error) {
      console.error("Error disconnecting integration:", error);
      toast({
        title: "Error",
        description: "Kunne ikke koble fra integrasjon",
        variant: "destructive",
      });
    } finally {
      setIsConnecting(null);
    }
  };

  function onSubmit(data: NotificationsFormValues) {
    toast({
      title: "You submitted the following values:",
      description: (
        <pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
          <code className="text-white">{JSON.stringify(data, null, 2)}</code>
        </pre>
      ),
    });
  }

  return (
    <Card>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <div>
              <h3 className="mb-4 text-lg font-medium">Integrasjoner</h3>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="text-muted-foreground">Laster integrasjoner...</div>
                </div>
              ) : (
                <div className="space-y-4">
                  <FormField
                    control={form.control}
                    name="google_calendar"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start justify-between rounded-lg border p-4">
                        <div className="space-y-0.5">
                          <FormLabel className="text-base text-nowrap">
                            <Icons.ggcalendar className="h-6 w-6" /> Google
                            kalender
                          </FormLabel>
                          <div className="p-3 text-xs">
                            <FormDescription>
                              Få tilgang på alle dine bookinger i sentral kalender.
                              Nye funksjoner med Ciri-bookinger kommer også.
                            </FormDescription>
                            {integrationStatus.google_calendar && (
                              <div className="mt-2 text-xs text-green-600 dark:text-green-400">
                                Koblet til Google Calendar
                              </div>
                            )}
                          </div>
                        </div>
                        <FormControl>
                          {integrationStatus.google_calendar ? (
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDisconnect('google_calendar')}
                                disabled={isConnecting === 'google_calendar'}
                              >
                                {isConnecting === 'google_calendar' ? 'Kobler fra...' : 'Koble fra'}
                              </Button>
                            </div>
                          ) : (
                            <Button 
                              className="dark:text-white"
                              onClick={() => handleConnect('google_calendar')}
                              disabled={isConnecting === 'google_calendar'}
                            >
                              {isConnecting === 'google_calendar' ? 'Kobler til...' : 'Koble til'}
                            </Button>
                          )}
                        </FormControl>
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="google_email"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start justify-between rounded-lg border p-4">
                        <div className="space-y-0.5">
                          <FormLabel className="text-base text-nowrap">
                            <Icons.gmail className="h-6 w-6" /> Gmail
                          </FormLabel>
                          <div className="p-3 text-xs">
                            <FormDescription>
                              Koble opp Gmail kontoen din for automatisk håndtering
                              av innkommende henvendelser.
                            </FormDescription>
                            {integrationStatus.google_email && companyData?.gmail_box_email && (
                              <div className="mt-2 text-xs text-green-600 dark:text-green-400">
                                Koblet til: {companyData.gmail_box_email}
                              </div>
                            )}
                          </div>
                        </div>
                        <FormControl>
                          {integrationStatus.google_email ? (
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDisconnect('google_email')}
                                disabled={isConnecting === 'google_email'}
                              >
                                {isConnecting === 'google_email' ? 'Kobler fra...' : 'Koble fra'}
                              </Button>
                            </div>
                          ) : (
                            <div className="flex flex-col items-end gap-2">
                              <Input
                                type="password"
                                placeholder="Enter Gmail app password"
                                value={gmailAppPassword}
                                onChange={(e) => setGmailAppPassword(e.target.value)}
                                className="w-64"
                              />
                              <Button 
                                className="dark:text-white"
                                onClick={() => handleConnect('google_email')}
                                disabled={isConnecting === 'google_email' || !gmailAppPassword}
                              >
                                {isConnecting === 'google_email' ? 'Kobler til...' : 'Koble til'}
                              </Button>
                            </div>
                          )}
                        </FormControl>
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="outlook_email"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start justify-between rounded-lg border p-4">
                        <div className="space-y-0.5">
                          <FormLabel className="text-base text-nowrap">
                            <Icons.outlook className="h-6 w-6" /> Outlook
                          </FormLabel>
                          <div className="p-3 text-xs">
                            <FormDescription>
                              Koble opp Outlook kontoen din for automatisk
                              håndtering av innkommende henvendelser.
                            </FormDescription>
                            {integrationStatus.outlook_email && companyData?.outlook_box_email && (
                              <div className="mt-2 text-xs text-green-600 dark:text-green-400">
                                Koblet til: {companyData.outlook_box_email}
                              </div>
                            )}
                          </div>
                        </div>
                        <FormControl>
                          {integrationStatus.outlook_email ? (
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDisconnect('outlook_email')}
                                disabled={isConnecting === 'outlook_email'}
                              >
                                {isConnecting === 'outlook_email' ? 'Kobler fra...' : 'Koble fra'}
                              </Button>
                            </div>
                          ) : (
                            <Button 
                              className="dark:text-white"
                              onClick={() => handleConnect('outlook_email')}
                              disabled={isConnecting === 'outlook_email'}
                            >
                              {isConnecting === 'outlook_email' ? 'Kobler til...' : 'Koble til'}
                            </Button>
                          )}
                        </FormControl>
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="instagram"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start justify-between rounded-lg border p-4">
                        <div className="space-y-0.5">
                          <FormLabel className="text-base text-nowrap">
                            <Icons.instagram className="h-6 w-6" /> Instagram
                          </FormLabel>
                          <div className="p-3 text-xs">
                            <FormDescription>
                              Koble opp Instagram kontoen din for automatisk
                              håndtering av kommentarer og meldinger.
                            </FormDescription>
                            {integrationStatus.instagram && companyData?.instagram_username && (
                              <div className="mt-2 text-xs text-green-600 dark:text-green-400">
                                Koblet til: {companyData.instagram_username}
                              </div>
                            )}
                          </div>
                        </div>
                        <FormControl>
                          {integrationStatus.instagram ? (
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDisconnect('instagram')}
                                disabled={isConnecting === 'instagram'}
                              >
                                {isConnecting === 'instagram' ? 'Kobler fra...' : 'Koble fra'}
                              </Button>
                            </div>
                          ) : (
                            <Button 
                              className="dark:text-white"
                              onClick={() => handleConnect('instagram')}
                              disabled={isConnecting === 'instagram'}
                            >
                              {isConnecting === 'instagram' ? 'Kobler til...' : 'Koble til'}
                            </Button>
                          )}
                        </FormControl>
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="facebook"
                    render={({ field }) => (
                      <FormItem className="flex flex-row items-start justify-between rounded-lg border p-4">
                        <div className="space-y-0.5">
                          <FormLabel className="text-base text-nowrap">
                            <Icons.facebook className="h-6 w-6" /> Facebook
                          </FormLabel>
                          <div className="p-3 text-xs">
                            <FormDescription>
                              Koble opp Facebook siden din for automatisk
                              håndtering av meldinger og kommentarer.
                            </FormDescription>
                            {integrationStatus.facebook && companyData?.facebook_box_page_name && (
                              <div className="mt-2 text-xs text-green-600 dark:text-green-400">
                                Koblet til: {companyData.facebook_box_page_name}
                              </div>
                            )}
                          </div>
                        </div>
                        <FormControl>
                          {integrationStatus.facebook ? (
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleDisconnect('facebook')}
                                disabled={isConnecting === 'facebook'}
                              >
                                {isConnecting === 'facebook' ? 'Kobler fra...' : 'Koble fra'}
                              </Button>
                            </div>
                          ) : (
                            <Button 
                              className="dark:text-white"
                              onClick={() => handleConnect('facebook')}
                              disabled={isConnecting === 'facebook'}
                            >
                              {isConnecting === 'facebook' ? 'Kobler til...' : 'Koble til'}
                            </Button>
                          )}
                        </FormControl>
                      </FormItem>
                    )}
                  />
                </div>
              )}
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
