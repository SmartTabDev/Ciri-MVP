import React, { useEffect } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useFileUpload } from "@/hooks/use-file-upload";

interface TextContextFormProps {
  textContext: string;
  setTextContext: (val: string) => void;
  placeholder?: string;
  label?: string;
  description?: string;
  disabled?: boolean;
  maxLength?: number;
  minLength?: number;
}

export const TextContextForm: React.FC<TextContextFormProps> = ({ 
  textContext, 
  setTextContext, 
  placeholder = "Enter your company context here...",
  label = "Company Context",
  description = "Upload a text file or enter your company context manually",
  disabled = false,
  maxLength = 1000,
  minLength = 100
}) => {
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
            const content = e.target?.result as string || "";
            
            // Check length constraints
            if (content.length > maxLength) {
              setCustomError(`File content exceeds the maximum length of ${maxLength} characters.`);
              return;
            }
            
            if (content.length < minLength) {
              setCustomError(`File content must be at least ${minLength} characters long.`);
              return;
            }
            
            setTextContext(content);
            setCustomError(null);
          };
          reader.onerror = () => {
            setCustomError("Failed to read the file.");
          };
          reader.readAsText(file);
        } else {
          setCustomError("Only .txt files are supported.");
        }
      } else {
        setCustomError("Only .txt files are supported.");
      }
    } else {
      setCustomError(null);
    }
  }, [files, setTextContext, maxLength, minLength]);

  // Calculate character count (letters only, similar to the original implementation)
  const charCount = textContext.replace(/[^a-zA-ZæøåÆØÅ]/g, "").length;

  return (
    <div className="flex flex-col gap-6 w-full">
      <div className="w-full">
        <Label htmlFor="text-context-textarea">{label}</Label>
        <Textarea
          id="text-context-textarea"
          placeholder={placeholder}
          className="mt-2 min-h-[400px]"
          value={textContext}
          onChange={(e) => {
            const value = e.target.value;
            const len = value.replace(/[^a-zA-ZæøåÆØÅ]/g, "").length; // letters only
            
            // Always update the text context to allow typing
            setTextContext(value);
            
            // Check length constraints and set errors, but don't block input
            if (value.length > maxLength) {
              setCustomError(`Text exceeds the maximum length of ${maxLength} characters.`);
            } else if (len < minLength) {
              setCustomError(`Text must be at least ${minLength} characters long.`);
            } else {
              setCustomError(null);
            }
          }}
          disabled={disabled}
        />
        <div className="flex justify-between items-center mt-2">
          <p className="text-sm text-muted-foreground">
            Characters: {charCount} / {maxLength}
          </p>
          {textContext.length > 0 && (
            <p className="text-xs text-muted-foreground">
              Total characters: {textContext.length}
            </p>
          )}
        </div>
        <p className="text-muted-foreground/60 text-xs mt-1">
          {description}
        </p>
      </div>
      
      <div className="w-full flex flex-col gap-2">
        <div className="flex items-center justify-center">
          <input {...getInputProps()} style={{ display: 'none' }} />
          <Button 
            type="button" 
            variant="outline" 
            onClick={openFileDialog}
            disabled={disabled}
          >
            Upload Text File
          </Button>
          {files.length > 0 && (
            <div className="flex items-center gap-2 ml-4">
              <span className="text-sm text-muted-foreground">{files[0].file.name}</span>
              <Button 
                type="button" 
                size="sm" 
                variant="ghost" 
                onClick={() => removeFile(files[0].id)}
                disabled={disabled}
              >
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
