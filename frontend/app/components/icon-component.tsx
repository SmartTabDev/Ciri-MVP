import { icons } from "lucide-react";
import { Icon as IconifyIcon } from "@iconify/react";

type IconProps = {
  name: string;
  className?: string;
};

export type IconType = React.ComponentType<React.SVGProps<SVGSVGElement>>;

type IconsType = {
  [key: string]: IconType;
};

const iconMap: IconsType = icons;

const Icon: React.FC<IconProps> = ({ name, className }) => {
  if (!name) return null;
  if (name.includes(":")) {
    // Iconify icon
    return <IconifyIcon icon={name} className={className} />;
  }
  const LucideIcon = iconMap[name];

  if (!LucideIcon) {
    return null;
  }

  return <LucideIcon className={className} />;
};

export default Icon;
