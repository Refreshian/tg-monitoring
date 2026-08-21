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
  total?: number;
};
