import { FormEvent, useState } from "react";
import { DemoMentionFeed } from "@/features/preview/DemoMentionFeed";
import { PreviewSearchForm } from "@/features/preview/PreviewSearchForm";
import { VolumePriceEstimate } from "@/features/preview/VolumePriceEstimate";
import { QueryRewriteNotice } from "@/features/preview/QueryRewriteNotice";
import { MonitoringRequestForm } from "@/features/access-request/MonitoringRequestForm";
import { previewSearch } from "@/lib/api/preview";
import type { PreviewResponse } from "@/types/preview";

export function PreviewPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<PreviewResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await previewSearch(query);
      setResult(data);
      if (data.query && data.query !== query) {
        setQuery(data.query);
      }
    } catch {
      setError("Не удалось получить оценку. Попробуйте позже.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page">
      <div className="container page__inner page__inner--narrow">
        <h1>Оценка объёма и стоимости</h1>
        <p className="page__lead">
          Введите поисковый запрос обычным языком — при необходимости мы уточним его под правила
          поиска и покажем оценку объёма упоминаний и ориентировочную стоимость доступа. Тексты
          реальной выдачи на сайте не публикуются.
        </p>

        <PreviewSearchForm
          query={query}
          loading={loading}
          onQueryChange={setQuery}
          onSubmit={handleSearch}
        />

        {error && <p className="error">{error}</p>}
        {result && (
          <>
            {result.query_changed && result.original_query && (
              <QueryRewriteNotice
                originalQuery={result.original_query}
                query={result.query}
                note={result.query_note}
              />
            )}
            <VolumePriceEstimate
              query={result.query}
              weeklyCount={result.weekly_count}
              monthlyEstimate={result.estimated_monthly_messages}
              priceRub={result.estimated_price_rub}
              priceIsFrom={Boolean(result.price_is_from)}
            />
            <DemoMentionFeed />
            <MonitoringRequestForm
              key={result.query}
              title="Заявка на мониторинг"
              initialObject={result.query}
              query={result.query}
            />
          </>
        )}
      </div>
    </section>
  );
}
