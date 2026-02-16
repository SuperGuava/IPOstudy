"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/ipo", label: "IPO Pipeline" },
  { href: "/company/00126380", label: "Company Snapshot" },
  { href: "/quality", label: "Quality" },
  { href: "/export", label: "Export" },
];

export function AppShell({
  title,
  subtitle,
  rightSlot,
  children,
}: {
  title: string;
  subtitle?: string;
  rightSlot?: ReactNode;
  children: ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div data-testid="app-shell" className="min-h-screen text-ag-text">
      <div className="mx-auto grid min-h-screen max-w-[1600px] grid-cols-1 md:grid-cols-[240px_1fr]">
        <aside className="border-b border-ag-line bg-ag-panel/80 p-4 md:border-b-0 md:border-r">
          <div className="mb-5">
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-ag-accent">Antigravity</div>
            <div className="mt-1 text-sm text-ag-mute">Institutional Intelligence</div>
          </div>
          <nav aria-label="Primary" className="space-y-1">
            {navItems.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "block rounded-md border px-3 py-2 text-sm transition",
                    active
                      ? "border-ag-accent/40 bg-ag-accent/10 text-ag-text"
                      : "border-transparent text-ag-mute hover:border-ag-line hover:bg-ag-card hover:text-ag-text",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>

        <main className="p-4 md:p-6">
          <header className="mb-4 flex flex-col gap-2 border-b border-ag-line pb-4 md:flex-row md:items-end md:justify-between">
            <div>
              <h1 className="text-lg font-semibold md:text-xl">{title}</h1>
              {subtitle ? <p className="mt-1 text-xs text-ag-mute md:text-sm">{subtitle}</p> : null}
            </div>
            {rightSlot ? <div className="w-full md:w-auto">{rightSlot}</div> : null}
          </header>
          {children}
        </main>
      </div>
    </div>
  );
}
