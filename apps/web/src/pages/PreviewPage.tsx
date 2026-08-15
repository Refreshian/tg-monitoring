import { FormEvent, useState } from "react";
import { MentionList } from "@/features/preview/MentionList";
import { PreviewSearchForm } from "@/features/preview/PreviewSearchForm";
import { AccessRequestForm } from "@/features/access-request/AccessRequestForm";
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
    <section className="preview-page">
      <h1>Предпросмотр упоминаний</h1>
      <p className="lead">
        Введите поисковый запрос — мы покажем примеры найденных сообщений до подключения услуги.
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
          <AccessRequestForm query={result.query} />
        </>
      )}
    </section>
  );
}
