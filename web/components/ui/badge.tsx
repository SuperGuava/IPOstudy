import { cn } from "@/lib/utils";

const toneMap: Record<string, string> = {
  ok: "border-ag-ok/50 bg-ag-ok/10 text-ag-ok",
  warn: "border-ag-warn/50 bg-ag-warn/10 text-ag-warn",
  fail: "border-ag-fail/50 bg-ag-fail/10 text-ag-fail",
  muted: "border-ag-line bg-ag-panel text-ag-mute",
};

export function Badge({
  label,
  tone = "muted",
  className,
}: {
  label: string;
  tone?: "ok" | "warn" | "fail" | "muted";
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
        toneMap[tone],
        className,
      )}
    >
      {label}
    </span>
  );
}
