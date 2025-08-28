"use client";
import React, { useState, useMemo } from "react";
import { Check, Eye, EyeOff, X } from "lucide-react";
import { type FieldValues, ControllerRenderProps } from "react-hook-form";

// Constants
const PASSWORD_REQUIREMENTS = [
  { regex: /.{8,}/, text: "Minst 8 bokstaver" },
  { regex: /[0-9]/, text: "Minst 1 nummer" },
  { regex: /[a-z]/, text: "Minst én liten bokstav" },
  { regex: /[A-Z]/, text: "Minst én stor bokstav" },
  { regex: /[!-\/:-@[-`{-~]/, text: "Minst én spesiell bokstav" },
] as const;

type StrengthScore = 0 | 1 | 2 | 3 | 4 | 5;

const STRENGTH_CONFIG = {
  colors: {
    0: "bg-border",
    1: "bg-red-500",
    2: "bg-orange-500",
    3: "bg-amber-500",
    4: "bg-amber-700",
    5: "bg-emerald-500",
  } satisfies Record<StrengthScore, string>,
  texts: {
    0: "Skriv et passord",
    4: "Sterkt passord",
  } satisfies Record<Exclude<StrengthScore, number>, string>,
} as const;

type PasswordInputProps = ControllerRenderProps<FieldValues, "password"> &
  React.ComponentProps<"input">;

// Types
type Requirement = {
  met: boolean;
  text: string;
};

type PasswordStrength = {
  score: StrengthScore;
  requirements: Requirement[];
};

const PasswordInput = React.forwardRef<HTMLInputElement, PasswordInputProps>(
  ({ value, onChange, onBlur, name, ...rest }, ref) => {
    const [isVisible, setIsVisible] = useState(false);

    const calculateStrength = useMemo((): PasswordStrength => {
      const requirements = PASSWORD_REQUIREMENTS.map((req) => ({
        met: req.regex.test(value),
        text: req.text,
      }));

      return {
        score: requirements.filter((req) => req.met).length as StrengthScore,
        requirements,
      };
    }, [value]);

    // console.log(calculateStrength);

    return (
      <div className="mx-auto w-96">
        <form className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={isVisible ? "text" : "password"}
              value={value}
              onChange={onChange}
              onBlur={onBlur}
              placeholder="Password"
              aria-invalid={calculateStrength.score < 4}
              aria-describedby="password-strength"
              className="dark:bg-input/30 w-full rounded-[5px] border-2 bg-transparent p-2 text-base transition outline-none focus-within:border-blue-700"
              {...rest}
            />
            <button
              type="button"
              onClick={() => setIsVisible((prev) => !prev)}
              aria-label={isVisible ? "Hide password" : "Show password"}
              className="text-muted-foreground/80 hover:text-foreground absolute inset-y-0 right-0 flex w-9 items-center justify-center outline-none"
            >
              {isVisible ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
        </form>
        <div className="mt-2 flex w-full justify-between gap-2">
          <span
            className={`${
              calculateStrength.score >= 1 ? "bg-green-200" : "bg-border"
            } w-full rounded-full p-1`}
          ></span>
          <span
            className={`${
              calculateStrength.score >= 2 ? "bg-green-300" : "bg-border"
            } w-full rounded-full p-1`}
          ></span>
          <span
            className={`${
              calculateStrength.score >= 3 ? "bg-green-400" : "bg-border"
            } w-full rounded-full p-1`}
          ></span>
          <span
            className={`${
              calculateStrength.score >= 4 ? "bg-green-500" : "bg-border"
            } w-full rounded-full p-1`}
          ></span>
          <span
            className={`${
              calculateStrength.score >= 5 ? "bg-green-600" : "bg-border"
            } w-full rounded-full p-1`}
          ></span>
        </div>

        <p
          id="password-strength"
          className="my-2 flex justify-between text-sm font-medium"
        >
          <span>Må inneholde</span>
          <span>
            {
              STRENGTH_CONFIG.texts[
                Math.min(
                  calculateStrength.score,
                  4,
                ) as keyof typeof STRENGTH_CONFIG.texts
              ]
            }
          </span>
        </p>

        <ul className="space-y-1.5" aria-label="Password requirements">
          {calculateStrength.requirements.map((req, index) => (
            <li key={index} className="flex items-center space-x-2">
              {req.met ? (
                <Check size={16} className="text-emerald-500" />
              ) : (
                <X size={16} className="text-muted-foreground/80" />
              )}
              <span
                className={`text-xs ${
                  req.met ? "text-emerald-600" : "text-muted-foreground"
                }`}
              >
                {req.text}
                <span className="sr-only">
                  {req.met ? " - Requirement met" : " - Requirement not met"}
                </span>
              </span>
            </li>
          ))}
        </ul>
      </div>
    );
  },
);

PasswordInput.displayName = "PasswordInput";

export default PasswordInput;
