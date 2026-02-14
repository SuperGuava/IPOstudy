import { IpoBoard } from "@/components/ipo-board";
import { getIpoPipeline } from "@/lib/api";

export default async function IpoPage() {
  const items = await getIpoPipeline();
  return <IpoBoard items={items} />;
}
