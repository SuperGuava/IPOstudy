export type IpoItem = {
  pipeline_id: string;
  corp_name: string;
  stage: string;
  listing_date: string;
};

export async function getIpoPipeline(): Promise<IpoItem[]> {
  return [
    {
      pipeline_id: "alpha-ipo-1",
      corp_name: "알파테크",
      stage: "공모",
      listing_date: "2026-03-15",
    },
  ];
}

export async function getIpoDetail(pipelineId: string): Promise<IpoItem> {
  return {
    pipeline_id: pipelineId,
    corp_name: "알파테크",
    stage: "공모",
    listing_date: "2026-03-15",
  };
}

export async function getCompany(corpCode: string): Promise<{ corp_code: string; corp_name: string; market_cap: string }> {
  return {
    corp_code: corpCode,
    corp_name: "알파테크",
    market_cap: "423,849,000,000,000",
  };
}
