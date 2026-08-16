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
  total: number;
  items: MentionItem[];
  estimated_price_rub?: number | null;
  price_is_from?: boolean;
};
