export type IpoItem = {
  pipeline_id: string;
  corp_code: string | null;
  corp_name: string;
  stage: string;
  listing_date: string | null;
  lead_manager?: string | null;
  source_dart_rcept_no?: string | null;
};

export type RefreshMeta = {
  batch_id: string;
  published: boolean;
  issue_count: number;
  kind_rows: number;
  dart_rows: number;
  krx_rows: number;
  source_status: Record<string, string>;
};

export type QualityIssue = {
  id: number;
  source: string;
  rule_code: string;
  severity: string;
  entity_type: string;
  entity_key: string;
  message: string;
  batch_id: string | null;
  observed_at: string | null;
};

export type QualitySummary = {
  summary_date: string;
  source: string;
  pass_count: number;
  warn_count: number;
  fail_count: number;
  fail_rate: number;
};

export type QualityOverview = {
  total_issues: number;
  severity_counts: Record<string, number>;
  source_counts: Record<string, number>;
  top_rules: Array<{ rule_code: string; count: number }>;
};

export type QualityRuleMeta = {
  rule_code: string;
  source: string;
  severity: string;
  title: string;
  description: string;
  operator_action: string;
};

export type InsightCompanyItem = {
  company_key: string;
  corp_code: string | null;
  corp_name: string;
  stage: string;
  listing_date: string | null;
  lead_manager: string | null;
  quality: Record<string, number>;
  risk_label: "low" | "medium" | "high";
};

export type InsightCompanyDetail = {
  company_key: string;
  corp_code: string | null;
  corp_name: string;
  risk_label: "low" | "medium" | "high";
  ipo: {
    pipeline_id: string;
    stage: string;
    listing_date: string | null;
    lead_manager: string | null;
  };
  quality: {
    severity: Record<string, number>;
    source: Record<string, number>;
  };
  beginner_summary: string;
  quick_insights: string[];
};

export type InsightTemplate = {
  template_id: string;
  title: string;
  description: string;
  steps: string[];
};

export type InsightCompare = {
  items: InsightCompanyDetail[];
  total: number;
  summary: {
    max_fail: number;
    avg_warn: number;
    risk_distribution: Record<string, number>;
  };
};

export type InsightReport = {
  company_key: string;
  template_id: string;
  template_title: string;
  generated_at: string;
  report_lines: string[];
};

export type InsightOverview = {
  total_companies: number;
  stage_counts: Record<string, number>;
  risk_counts: Record<string, number>;
  top_lead_managers: Array<{ lead_manager: string; count: number }>;
};

type IpoPipelineResponse = {
  items: IpoItem[];
  total: number;
  refresh?: RefreshMeta;
};

type QualityIssueResponse = {
  items: QualityIssue[];
  total: number;
};

type QualitySummaryResponse = {
  items: QualitySummary[];
  total: number;
};

type QualityOverviewResponse = QualityOverview;

type QualityRuleCatalogResponse = {
  items: QualityRuleMeta[];
  total: number;
};

type InsightCompanyResponse = {
  items: InsightCompanyItem[];
  total: number;
};

type InsightTemplateResponse = {
  items: InsightTemplate[];
  total: number;
};

type InsightCompareResponse = InsightCompare;
type InsightReportResponse = InsightReport;
type InsightOverviewResponse = InsightOverview;

const API_BASE = process.env.API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function getIpoPipeline(options?: {
  refresh?: boolean;
  corpCode?: string;
  basDd?: string;
}): Promise<IpoPipelineResponse> {
  const query = new URLSearchParams();
  if (options?.refresh) {
    query.set("refresh", "true");
  }
  if (options?.corpCode) {
    query.set("corp_code", options.corpCode);
  }
  if (options?.basDd) {
    query.set("bas_dd", options.basDd);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return getJson<IpoPipelineResponse>(`/ipo/pipeline${suffix}`);
}

export async function getIpoDetail(pipelineId: string): Promise<IpoItem> {
  return getJson<IpoItem>(`/ipo/${pipelineId}`);
}

export async function getCompany(corpCode: string): Promise<{
  corp_code: string;
  profile?: { corp_name?: string };
  market?: { market_cap?: number };
}> {
  return getJson(`/company/snapshot?corp_code=${encodeURIComponent(corpCode)}`);
}

export async function getQualityIssues(options?: {
  source?: string;
  severity?: string;
  ruleCode?: string;
  fromDate?: string;
  toDate?: string;
}): Promise<QualityIssueResponse> {
  const query = new URLSearchParams();
  if (options?.source) {
    query.set("source", options.source);
  }
  if (options?.severity) {
    query.set("severity", options.severity);
  }
  if (options?.ruleCode) {
    query.set("rule_code", options.ruleCode);
  }
  if (options?.fromDate) {
    query.set("from", options.fromDate);
  }
  if (options?.toDate) {
    query.set("to", options.toDate);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return getJson<QualityIssueResponse>(`/quality/issues${suffix}`);
}

export async function getQualitySummary(options?: {
  source?: string;
  fromDate?: string;
  toDate?: string;
}): Promise<QualitySummaryResponse> {
  const query = new URLSearchParams();
  if (options?.source) {
    query.set("source", options.source);
  }
  if (options?.fromDate) {
    query.set("from", options.fromDate);
  }
  if (options?.toDate) {
    query.set("to", options.toDate);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return getJson<QualitySummaryResponse>(`/quality/summary${suffix}`);
}

export async function getQualityOverview(options?: {
  source?: string;
  fromDate?: string;
  toDate?: string;
}): Promise<QualityOverviewResponse> {
  const query = new URLSearchParams();
  if (options?.source) {
    query.set("source", options.source);
  }
  if (options?.fromDate) {
    query.set("from", options.fromDate);
  }
  if (options?.toDate) {
    query.set("to", options.toDate);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return getJson<QualityOverviewResponse>(`/quality/overview${suffix}`);
}

export async function getQualityRules(options?: {
  source?: string;
  severity?: string;
}): Promise<QualityRuleCatalogResponse> {
  const query = new URLSearchParams();
  if (options?.source) {
    query.set("source", options.source);
  }
  if (options?.severity) {
    query.set("severity", options.severity);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return getJson<QualityRuleCatalogResponse>(`/quality/rules${suffix}`);
}

export async function getInsightCompanies(options?: {
  query?: string;
  limit?: number;
  stage?: string;
  riskLabel?: "low" | "medium" | "high";
}): Promise<InsightCompanyResponse> {
  const query = new URLSearchParams();
  if (options?.query) {
    query.set("query", options.query);
  }
  if (options?.limit) {
    query.set("limit", String(options.limit));
  }
  if (options?.stage) {
    query.set("stage", options.stage);
  }
  if (options?.riskLabel) {
    query.set("risk_label", options.riskLabel);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return getJson<InsightCompanyResponse>(`/insights/companies${suffix}`);
}

export async function getInsightCompany(companyKey: string): Promise<InsightCompanyDetail> {
  return getJson<InsightCompanyDetail>(`/insights/company?company_key=${encodeURIComponent(companyKey)}`);
}

export async function getInsightTemplates(): Promise<InsightTemplateResponse> {
  return getJson<InsightTemplateResponse>("/insights/templates");
}

export async function getInsightCompare(companyKeys: string[]): Promise<InsightCompareResponse> {
  const query = new URLSearchParams();
  for (const key of companyKeys) {
    query.append("company_key", key);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return getJson<InsightCompareResponse>(`/insights/compare${suffix}`);
}

export async function getInsightReport(companyKey: string, templateId: string): Promise<InsightReportResponse> {
  const query = new URLSearchParams({ company_key: companyKey, template_id: templateId });
  return getJson<InsightReportResponse>(`/insights/report?${query.toString()}`);
}

export async function getInsightOverview(): Promise<InsightOverviewResponse> {
  return getJson<InsightOverviewResponse>("/insights/overview");
}
