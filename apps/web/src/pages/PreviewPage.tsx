import { FormEvent, useState } from "react";
import { MentionList } from "@/features/preview/MentionList";
import { PreviewSearchForm } from "@/features/preview/PreviewSearchForm";
import { PriceEstimate } from "@/features/preview/PriceEstimate";
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
    } catch {
      setError("Не удалось получить предпросмотр. Попробуйте позже.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="page">
      <div className="container page__inner page__inner--narrow">
        <h1>Предпросмотр упоминаний</h1>
        <p className="page__lead">
          Введите поисковый запрос — покажем последние найденные упоминания до подключения
          услуги.
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
            <MentionList result={result} />
            {result.estimated_price_rub != null && result.estimated_price_rub > 0 && (
              <PriceEstimate
                priceRub={result.estimated_price_rub}
                priceIsFrom={Boolean(result.price_is_from)}
              />
            )}
            <MonitoringRequestForm
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
