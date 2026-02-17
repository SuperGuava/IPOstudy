import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import { getInsightCompanies, getInsightCompany, getInsightTemplates } from "@/lib/api";

function textParam(value: string | string[] | undefined): string {
  return typeof value === "string" ? value : "";
}

export default async function ExplorerPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const query = textParam(params.q);
  const selectedKeyFromQuery = textParam(params.company_key);

  const [companies, templates] = await Promise.all([
    getInsightCompanies({ query: query || undefined, limit: 40 }).catch(() => ({ items: [], total: 0 })),
    getInsightTemplates().catch(() => ({ items: [], total: 0 })),
  ]);

  const selectedKey = selectedKeyFromQuery || companies.items[0]?.company_key || "";
  const detail = selectedKey ? await getInsightCompany(selectedKey).catch(() => null) : null;

  return (
    <AppShell title="Company Explorer" subtitle="IPO beyond view: beginner-first company discovery and analysis">
      <Card className="mb-4">
        <form className="grid gap-3 md:grid-cols-[1fr_auto]">
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">search company</span>
            <input
              name="q"
              defaultValue={query}
              placeholder="회사명 또는 corp_code"
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            />
          </label>
          <div className="flex items-end">
            <button
              type="submit"
              className="rounded-md border border-ag-accent/50 bg-ag-accent/10 px-3 py-1.5 text-xs font-semibold text-ag-accent hover:bg-ag-accent/20"
            >
              Search
            </button>
          </div>
        </form>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[380px_1fr]">
        <Card>
          <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Company List</div>
          <ul className="space-y-2">
            {companies.items.map((item) => {
              const active = item.company_key === selectedKey;
              return (
                <li key={item.company_key}>
                  <Link
                    href={`/explorer?${new URLSearchParams({ q: query, company_key: item.company_key }).toString()}`}
                    className={`block rounded border px-2 py-2 text-xs ${
                      active
                        ? "border-ag-accent/50 bg-ag-accent/10 text-ag-text"
                        : "border-ag-line bg-ag-panel/70 text-ag-mute hover:border-ag-accent/40 hover:text-ag-text"
                    }`}
                  >
                    <div className="font-semibold">{item.corp_name}</div>
                    <div className="mt-1">
                      stage: {item.stage} | risk: {item.risk_label}
                    </div>
                    <div className="text-ag-mute">listing: {item.listing_date ?? "-"}</div>
                  </Link>
                </li>
              );
            })}
            {companies.items.length === 0 ? <li className="text-xs text-ag-mute">No companies found.</li> : null}
          </ul>
        </Card>

        <div className="space-y-4">
          <Card>
            <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Beginner Summary</div>
            {detail ? (
              <div className="space-y-2 text-sm">
                <div className="font-semibold">{detail.corp_name}</div>
                <div>{detail.beginner_summary}</div>
                <div className="text-xs text-ag-mute">
                  stage: {detail.ipo.stage} | listing: {detail.ipo.listing_date ?? "-"} | lead:{" "}
                  {detail.ipo.lead_manager ?? "-"}
                </div>
              </div>
            ) : (
              <div className="text-xs text-ag-mute">Select a company to see analysis.</div>
            )}
          </Card>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Quick Insights</div>
              <ul className="space-y-2 text-xs">
                {detail?.quick_insights.map((line, idx) => (
                  <li key={idx} className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                    {line}
                  </li>
                )) ?? <li className="text-ag-mute">No insights available.</li>}
              </ul>
            </Card>

            <Card>
              <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Quality Snapshot</div>
              <ul className="space-y-2 text-xs">
                {detail ? (
                  <>
                    <li className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                      FAIL: {detail.quality.severity.FAIL ?? 0}
                    </li>
                    <li className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                      WARN: {detail.quality.severity.WARN ?? 0}
                    </li>
                    <li className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                      PASS: {detail.quality.severity.PASS ?? 0}
                    </li>
                  </>
                ) : (
                  <li className="text-ag-mute">No quality summary.</li>
                )}
              </ul>
            </Card>
          </div>

          <Card>
            <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Analysis Templates</div>
            <ul className="space-y-2 text-xs">
              {templates.items.map((template) => (
                <li key={template.template_id} className="rounded border border-ag-line bg-ag-panel/70 p-2">
                  <div className="font-semibold">{template.title}</div>
                  <div className="mt-1 text-ag-mute">{template.description}</div>
                  <div className="mt-1">{template.steps.join(" / ")}</div>
                </li>
              ))}
              {templates.items.length === 0 ? <li className="text-ag-mute">No templates configured.</li> : null}
            </ul>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}

