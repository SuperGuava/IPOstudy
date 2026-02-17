import Link from "next/link";

import { AppShell } from "@/components/app-shell";
import { Card } from "@/components/ui/card";
import {
  getInsightCompanies,
  getInsightCompany,
  getInsightCompare,
  getInsightOverview,
  getInsightReport,
  getInsightTemplates,
  getInsightValidation,
} from "@/lib/api";

function textParam(value: string | string[] | undefined): string {
  return typeof value === "string" ? value : "";
}

function buildExplorerHref(params: {
  q?: string;
  companyKey?: string;
  compare?: string;
  stage?: string;
  risk?: string;
  templateId?: string;
}): string {
  const query = new URLSearchParams();
  if (params.q) query.set("q", params.q);
  if (params.companyKey) query.set("company_key", params.companyKey);
  if (params.compare) query.set("compare", params.compare);
  if (params.stage) query.set("stage", params.stage);
  if (params.risk) query.set("risk", params.risk);
  if (params.templateId) query.set("template_id", params.templateId);
  return `/explorer?${query.toString()}`;
}

export default async function ExplorerPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const query = textParam(params.q);
  const stage = textParam(params.stage);
  const risk = textParam(params.risk) as "" | "low" | "medium" | "high";
  const selectedKeyFromQuery = textParam(params.company_key);
  const compareRaw = textParam(params.compare);
  const templateId = textParam(params.template_id) || "foundation-check";

  const compareKeys = compareRaw
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean)
    .slice(0, 3);

  const [companies, templates, overview, validation] = await Promise.all([
    getInsightCompanies({
      query: query || undefined,
      stage: stage || undefined,
      riskLabel: risk || undefined,
      limit: 40,
    }).catch(() => ({ items: [], total: 0 })),
    getInsightTemplates().catch(() => ({ items: [], total: 0 })),
    getInsightOverview().catch(() => ({
      total_companies: 0,
      stage_counts: {},
      risk_counts: { low: 0, medium: 0, high: 0 },
      top_lead_managers: [],
    })),
    getInsightValidation().catch(() => ({
      status: "unknown",
      approval_conditions: [],
      kill_criteria: [],
      budget: {
        legal_review_usd: 0,
        landing_ads_usd: 0,
        infra_12m_usd: 0,
        total_1y_usd: 0,
        revenue_1y_usd: 0,
        pnl_1y_usd: 0,
      },
    })),
  ]);

  const selectedKey = selectedKeyFromQuery || companies.items[0]?.company_key || "";
  const stageCounts = overview.stage_counts as Record<string, number>;
  const riskCounts = overview.risk_counts as Record<string, number>;
  const [detail, compareData, report] = await Promise.all([
    selectedKey ? getInsightCompany(selectedKey).catch(() => null) : Promise.resolve(null),
    compareKeys.length >= 2 ? getInsightCompare(compareKeys).catch(() => null) : Promise.resolve(null),
    selectedKey ? getInsightReport(selectedKey, templateId).catch(() => null) : Promise.resolve(null),
  ]);

  return (
    <AppShell title="Company Explorer" subtitle="Beginner-first company discovery, compare, and guided analysis">
      <div className="mb-4 grid gap-4 md:grid-cols-4">
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Total Companies</div>
          <div className="mt-2 text-2xl font-semibold">{overview.total_companies}</div>
        </Card>
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Listed</div>
          <div className="mt-2 text-2xl font-semibold">{stageCounts["listed"] ?? 0}</div>
        </Card>
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">Prelisting</div>
          <div className="mt-2 text-2xl font-semibold">{stageCounts["prelisting"] ?? 0}</div>
        </Card>
        <Card>
          <div className="text-[11px] uppercase tracking-wide text-ag-mute">High Risk</div>
          <div className="mt-2 text-2xl font-semibold">{riskCounts["high"] ?? 0}</div>
        </Card>
      </div>

      <Card className="mb-4">
        <form className="grid gap-3 md:grid-cols-[1fr_170px_150px_190px_auto]">
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">search company</span>
            <input
              name="q"
              defaultValue={query}
              placeholder="company name or corp_code"
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">stage</span>
            <select
              name="stage"
              defaultValue={stage}
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            >
              <option value="">all</option>
              <option value="offering">offering</option>
              <option value="prelisting">prelisting</option>
              <option value="listed">listed</option>
            </select>
          </label>
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">risk</span>
            <select
              name="risk"
              defaultValue={risk}
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            >
              <option value="">all</option>
              <option value="low">low</option>
              <option value="medium">medium</option>
              <option value="high">high</option>
            </select>
          </label>
          <label className="block">
            <span className="mb-1 block text-[11px] uppercase tracking-wide text-ag-mute">template</span>
            <select
              name="template_id"
              defaultValue={templateId}
              className="w-full rounded-md border border-ag-line bg-ag-card px-2 py-1.5 text-sm outline-none focus:border-ag-accent"
            >
              {templates.items.map((template) => (
                <option key={template.template_id} value={template.template_id}>
                  {template.title}
                </option>
              ))}
            </select>
          </label>
          <div className="flex items-end">
            <button
              type="submit"
              className="rounded-md border border-ag-accent/50 bg-ag-accent/10 px-3 py-1.5 text-xs font-semibold text-ag-accent hover:bg-ag-accent/20"
            >
              Apply
            </button>
          </div>
        </form>
      </Card>

      <div className="grid gap-4 xl:grid-cols-[400px_1fr]">
        <Card>
          <div className="mb-2 flex items-center justify-between text-[11px] uppercase tracking-wide text-ag-mute">
            <span>Company List</span>
            <span>{companies.total} rows</span>
          </div>
          <ul className="space-y-2">
            {companies.items.map((item) => {
              const active = item.company_key === selectedKey;
              const isCompared = compareKeys.includes(item.company_key);
              const nextCompare = isCompared
                ? compareKeys.filter((key) => key !== item.company_key)
                : [...compareKeys, item.company_key].slice(-3);
              return (
                <li key={item.company_key} className="rounded border border-ag-line bg-ag-panel/70 p-2">
                  <Link
                    href={buildExplorerHref({
                      q: query,
                      stage,
                      risk,
                      templateId,
                      companyKey: item.company_key,
                      compare: compareKeys.join(","),
                    })}
                    className={`block rounded border px-2 py-1.5 text-xs ${
                      active
                        ? "border-ag-accent/50 bg-ag-accent/10 text-ag-text"
                        : "border-transparent text-ag-mute hover:border-ag-accent/40 hover:text-ag-text"
                    }`}
                  >
                    <div className="font-semibold">{item.corp_name}</div>
                    <div className="mt-1">
                      stage: {item.stage} | risk: {item.risk_label}
                    </div>
                    <div className="text-ag-mute">listing: {item.listing_date ?? "-"}</div>
                  </Link>
                  <div className="mt-2 flex items-center justify-between text-[11px]">
                    <span className="text-ag-mute">FAIL {item.quality.FAIL ?? 0}</span>
                    <Link
                      href={buildExplorerHref({
                        q: query,
                        stage,
                        risk,
                        templateId,
                        companyKey: selectedKey || item.company_key,
                        compare: nextCompare.join(","),
                      })}
                      className="rounded border border-ag-line px-2 py-1 text-ag-mute hover:border-ag-accent/40 hover:text-ag-text"
                    >
                      {isCompared ? "Remove Compare" : "Add Compare"}
                    </Link>
                  </div>
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
                <div className="font-semibold">
                  {detail.corp_name} ({detail.risk_label} risk)
                </div>
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
              <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Beginner Report</div>
              {report ? (
                <div className="space-y-2 text-xs">
                  <div className="font-semibold">{report.template_title}</div>
                  <div className="text-ag-mute">generated: {report.generated_at}</div>
                  {report.report_lines.map((line, idx) => (
                    <div key={idx} className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                      {line}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-ag-mute">No report available.</div>
              )}
            </Card>

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
          </div>

          <Card>
            <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Compare Snapshot</div>
            {compareData && compareData.total >= 2 ? (
              <div className="space-y-2 text-xs">
                <div className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                  max FAIL: {compareData.summary.max_fail} | avg WARN: {compareData.summary.avg_warn}
                </div>
                <div className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                  risk distribution: low {compareData.summary.risk_distribution.low ?? 0}, medium{" "}
                  {compareData.summary.risk_distribution.medium ?? 0}, high{" "}
                  {compareData.summary.risk_distribution.high ?? 0}
                </div>
                <div className="grid gap-2 lg:grid-cols-3">
                  {compareData.items.map((item) => (
                    <div key={item.company_key} className="rounded border border-ag-line bg-ag-panel/70 p-2">
                      <div className="font-semibold">{item.corp_name}</div>
                      <div className="mt-1 text-ag-mute">stage: {item.ipo.stage}</div>
                      <div>FAIL {item.quality.severity.FAIL ?? 0}</div>
                      <div>WARN {item.quality.severity.WARN ?? 0}</div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-xs text-ag-mute">Select at least 2 companies with Add Compare.</div>
            )}
          </Card>

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

          <Card>
            <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Top Lead Managers</div>
            <ul className="space-y-2 text-xs">
              {overview.top_lead_managers.map((row) => (
                <li key={row.lead_manager} className="flex items-center justify-between rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                  <span>{row.lead_manager}</span>
                  <span className="font-mono text-ag-mute">{row.count}</span>
                </li>
              ))}
              {overview.top_lead_managers.length === 0 ? <li className="text-ag-mute">No lead manager data.</li> : null}
            </ul>
          </Card>

          <Card>
            <div className="mb-2 text-[11px] uppercase tracking-wide text-ag-mute">Validation Gate</div>
            <div className="mb-2 text-xs">
              Status: <span className="font-semibold">{validation.status}</span>
            </div>
            <div className="grid gap-2 lg:grid-cols-2">
              <div>
                <div className="mb-1 text-[11px] uppercase tracking-wide text-ag-mute">Approval Conditions</div>
                <ul className="space-y-1 text-xs">
                  {validation.approval_conditions.map((line, idx) => (
                    <li key={idx} className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                      {line}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <div className="mb-1 text-[11px] uppercase tracking-wide text-ag-mute">Kill Criteria</div>
                <ul className="space-y-1 text-xs">
                  {validation.kill_criteria.map((line, idx) => (
                    <li key={idx} className="rounded border border-ag-line bg-ag-panel/70 px-2 py-1.5">
                      {line}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="mt-2 rounded border border-ag-line bg-ag-panel/70 p-2 text-xs">
              Budget: legal ${validation.budget.legal_review_usd}, ads ${validation.budget.landing_ads_usd}, infra $
              {validation.budget.infra_12m_usd}, total ${validation.budget.total_1y_usd}, revenue $
              {validation.budget.revenue_1y_usd}, pnl ${validation.budget.pnl_1y_usd}
            </div>
          </Card>
        </div>
      </div>
    </AppShell>
  );
}
