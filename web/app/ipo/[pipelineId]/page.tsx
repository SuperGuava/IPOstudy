import { IpoDetail } from "@/components/ipo-detail";
import { getIpoDetail } from "@/lib/api";

export default async function IpoDetailPage({
  params,
}: {
  params: Promise<{ pipelineId: string }>;
}) {
  const { pipelineId } = await params;
  const item = await getIpoDetail(pipelineId);
  return <IpoDetail item={item} />;
}
