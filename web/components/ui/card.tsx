import type { HTMLAttributes, ReactNode } from "react";

import { cn } from "@/lib/utils";

export function Card({
  className,
  children,
  ...props
}: { className?: string; children: ReactNode } & HTMLAttributes<HTMLElement>) {
  return (
    <section
      {...props}
      className={cn(
        "rounded-xl border border-ag-line bg-ag-card/90 p-4 shadow-panel backdrop-blur-sm",
        className,
      )}
    >
      {children}
    </section>
  );
}
