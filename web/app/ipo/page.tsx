import { AppShell } from "@/components/app-shell";
import { IpoBoard } from "@/components/ipo-board";
import { getIpoPipeline } from "@/lib/api";

function normalizeBasDd(raw?: string): string {
  if (!raw) {
    return new Date().toISOString().slice(0, 10).replaceAll("-", "");
  }
  return raw.replaceAll("-", "");
}

export default async function IpoPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const refresh = params.refresh === "true";
  const corpCode = typeof params.corp_code === "string" ? params.corp_code : "00126380";
  const basDd = normalizeBasDd(typeof params.bas_dd === "string" ? params.bas_dd : undefined);

  const data = await getIpoPipeline({
    refresh,
    corpCode,
    basDd,
  });

  return (
    <AppShell
      title="IPO Pipeline"
      subtitle="High-density strategy surface for offering monitoring and source diagnostics"
    >
      <IpoBoard items={data.items} refresh={data.refresh} corpCode={corpCode} basDd={basDd} />
    </AppShell>
  );
}
