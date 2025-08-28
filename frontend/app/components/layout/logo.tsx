import Image from "next/image";

export default function Logo() {
  return (
    <Image
      src="/thecirilogo.png"
      width={100}
      height={100}
      className="me-1 rounded-sm transition-all group-data-collapsible:size-10 group-data-[collapsible=icon]:size-8"
      alt="shadcn ui kit logo"
    />
  );
}
