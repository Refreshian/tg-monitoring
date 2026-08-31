export type MentionTeaser = {
  source: string;
  url?: string | null;
  published_at?: string | null;
};

export type MentionItem = {
  source: string;
  title?: string | null;
  text: string;
  url?: string | null;
  published_at?: string | null;
};

export type PreviewResponse = {
  query: string;
  original_query?: string | null;
  query_changed?: boolean;
  query_note?: string | null;
  weekly_count?: number | null;
  estimated_monthly_messages?: number | null;
  estimated_price_rub?: number | null;
  price_is_from?: boolean;
  tariff_name?: string | null;
  sample_token?: string | null;
  samples_available?: boolean;
  teasers?: MentionTeaser[];
  total?: number;
};

export type SendSamplesResponse = {
  sent: boolean;
  message: string;
};

export type PreviewSamplesResponse = {
  query: string;
  items: MentionItem[];
  expires_note?: string;
};
