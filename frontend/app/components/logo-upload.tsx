"use client";

import { CircleUserRoundIcon, XIcon } from "lucide-react";
import { useEffect, useState } from "react";
import { toast } from "sonner";

import { useFileUpload } from "@/hooks/use-file-upload";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { companyService } from "@/services/company-service";
import { useUser } from "@/contexts/user-context";

interface LogoUploadProps {
  onLogoChange?: (logoUrl: string | null) => void;
}

export function LogoUpload({ onLogoChange }: LogoUploadProps) {
  const { user } = useUser();
  const [currentLogoUrl, setCurrentLogoUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const [{ files }, { removeFile, openFileDialog, getInputProps }] =
    useFileUpload({
      accept: "image/*",
      maxSize: 5 * 1024 * 1024, // 5MB limit
      onFilesAdded: async (addedFiles) => {
        if (addedFiles.length > 0 && user?.company_id) {
          await handleLogoUpload(addedFiles[0].file as File);
        }
      },
    });

  // Load existing logo when component mounts
  useEffect(() => {
    const loadLogo = async () => {
      if (!user?.company_id) return;
      
      try {
        const logoUrl = await companyService.getLogo(user.company_id);
        setCurrentLogoUrl(logoUrl);
        onLogoChange?.(logoUrl);
      } catch (error) {
        console.error('Error loading logo:', error);
      }
    };

    loadLogo();
  }, [user?.company_id, onLogoChange]);

  const handleLogoUpload = async (file: File) => {
    if (!user?.company_id) {
      toast.error("Ingen bedrift funnet");
      return;
    }

    setIsUploading(true);
    try {
      const response = await companyService.uploadLogo(user.company_id, file);
      
      if (response.success && response.logo_url) {
        setCurrentLogoUrl(response.logo_url);
        onLogoChange?.(response.logo_url);
        toast.success("Logo opplastet");
      } else {
        toast.error(response.message || "Kunne ikke laste opp logo");
      }
    } catch (error: any) {
      console.error('Error uploading logo:', error);
      toast.error(error.message || "Kunne ikke laste opp logo");
    } finally {
      setIsUploading(false);
    }
  };

  const handleRemoveLogo = () => {
    setCurrentLogoUrl(null);
    onLogoChange?.(null);
    removeFile(files[0]?.id);
  };

  const previewUrl = files[0]?.preview || currentLogoUrl;
  const fileName = files[0]?.file.name || null;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative inline-flex">
        <Button
          variant="outline"
          className="relative size-16 overflow-hidden p-0 shadow-none"
          onClick={openFileDialog}
          disabled={isUploading}
          aria-label={previewUrl ? "Change image" : "Upload image"}
        >
          {isUploading ? (
            <div className="flex items-center justify-center size-full">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-900 dark:border-white"></div>
            </div>
          ) : previewUrl ? (
            <img
              className="size-full object-cover"
              src={previewUrl}
              alt="Company logo"
              width={64}
              height={64}
              style={{ objectFit: "cover" }}
            />
          ) : (
            <div aria-hidden="true">
              <CircleUserRoundIcon className="size-4 opacity-60" />
            </div>
          )}
        </Button>
        {previewUrl && !isUploading && (
          <Button
            onClick={handleRemoveLogo}
            size="icon"
            className="border-background focus-visible:border-background absolute -top-2 -right-2 size-6 rounded-full border-2 shadow-none"
            aria-label="Remove image"
          >
            <XIcon className="size-3.5" />
          </Button>
        )}
        <input
          {...getInputProps()}
          className="sr-only"
          aria-label="Upload image file"
          tabIndex={-1}
          disabled={isUploading}
        />
      </div>
      {fileName && <p className="text-muted-foreground text-xs">{fileName}</p>}
      <p
        aria-live="polite"
        role="region"
        className="text-muted-foreground mt-2 text-xs"
      >
        {isUploading ? "Laster opp..." : "Din logo"}
      </p>
    </div>
  );
}
