import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export default function ExportPage() {
  return (
    <AppShell title="Export" subtitle="Download spreadsheet outputs from latest snapshot">
      <Card>
        <div className="flex flex-wrap gap-2">
          <Link
            href={`${API_BASE}/export/ipo.xlsx`}
            className="rounded-md border border-ag-line px-3 py-1.5 text-xs hover:border-ag-accent/50"
          >
            Download IPO XLSX
          </Link>
          <Link
            href={`${API_BASE}/export/company/00126380.xlsx`}
            className="rounded-md border border-ag-line px-3 py-1.5 text-xs hover:border-ag-accent/50"
          >
            Download Company XLSX
          </Link>
        </div>
      </Card>
    </AppShell>
  );
}
