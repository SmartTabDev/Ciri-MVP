import React, { useEffect } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useFileUpload } from "@/hooks/use-file-upload";

interface OnboardingTermsFormProps {
  terms: string;
  setTerms: (val: string) => void;
}

export const OnboardingTermsForm: React.FC<OnboardingTermsFormProps> = ({ terms, setTerms }) => {
  const [customError, setCustomError] = React.useState<string | null>(null);
  const [
    { files, errors },
    { getInputProps, openFileDialog, removeFile }
  ] = useFileUpload({
    accept: ".txt",
    multiple: false,
    maxSize: 5 * 1024 * 1024, // 5MB
  });

  useEffect(() => {
    if (files.length > 0) {
      const file = files[0].file;
      if (file instanceof File) {
        if (file.name.endsWith(".txt")) {
          const reader = new FileReader();
          reader.onload = (e) => {
            setTerms(e.target?.result as string || "");
            setCustomError(null);
          };
          reader.onerror = () => {
            setCustomError("Failed to read the file.");
          };
          reader.readAsText(file);
        } else {
          setCustomError("Only .txt files are supported.");
          setTerms("");
        }
      } else {
        setCustomError("Only .txt files are supported.");
        setTerms("");
      }
    } else {
      setCustomError(null);
    }
  }, [files, setTerms]);

  return (
    <div className="flex flex-col items-center gap-6 mt-8 w-full max-w-xl">
      <div className="w-xl">
        <Textarea
          id="terms-textarea"
          placeholder="Enter your company terms of service here..."
          className="mt-2 min-h-[250px]"
          value={terms}
          onChange={(e) => setTerms(e.target.value)}
        />
      </div>
      <div className="w-full flex flex-col gap-2">
        <div className="flex items-center justify-center">
          <input {...getInputProps()} style={{ display: 'none' }} />
          <Button type="button" variant="outline" onClick={openFileDialog}>
            Upload File
          </Button>
          {files.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-sm">{files[0].file.name}</span>
              <Button type="button" size="sm" variant="ghost" onClick={() => removeFile(files[0].id)}>
                Remove
              </Button>
            </div>
          )}
        </div>
        {(errors.length > 0 || customError) && (
          <div className="text-destructive text-sm mt-1">
            {errors.map((err, idx) => (
              <div key={idx}>{err}</div>
            ))}
            {customError && <div>{customError}</div>}
          </div>
        )}
      </div>
    </div>
  );
}; 