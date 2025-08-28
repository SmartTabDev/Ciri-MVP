export const DEFAULT_THEME = {
  preset: "default",
  radius: "default",
  scale: "none",
  contentLayout: "full",
} as const;

export type ThemeType = typeof DEFAULT_THEME;

export const THEMES = [
  {
    name: "Standard",
    value: "default",
    colors: ["oklch(0.33 0 0)"],
  },
  {
    name: "Minimalistisk",
    value: "lavender-dream",
    colors: ["oklch(0.71 0.16 293.54)"],
  },
];
