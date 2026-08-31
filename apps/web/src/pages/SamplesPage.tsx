import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { HighlightedText } from "@/components/HighlightedText";
import { fetchPreviewSamples } from "@/lib/api/preview";
import type { PreviewSamplesResponse } from "@/types/preview";

function formatPublished(value: string | null | undefined): string | null {
  if (!value) {
    return null;
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return null;
  }
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function SamplesPage() {
  const { token } = useParams<{ token: string }>();
  const [data, setData] = useState<PreviewSamplesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    document.title = "Примеры упоминаний — TG-Monitoring";
    const meta = document.createElement("meta");
    meta.name = "robots";
    meta.content = "noindex, nofollow";
    document.head.appendChild(meta);
    return () => {
      document.head.removeChild(meta);
    };
  }, []);

  useEffect(() => {
    if (!token) {
      setError("Ссылка недействительна.");
      setLoading(false);
      return;
    }

    let cancelled = false;
    fetchPreviewSamples(token)
      .then((response) => {
        if (!cancelled) {
          setData(response);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError("Примеры не найдены или срок ссылки истёк.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  return (
    <section className="page">
      <div className="container page__inner page__inner--narrow">
        <h1>Примеры упоминаний</h1>
        {loading && <p>Загружаем примеры…</p>}
        {error && <p className="error">{error}</p>}
        {data && (
          <>
            <p className="page__lead">
              Запрос: <code>{data.query}</code>
            </p>
            <p className="samples-page__note">
              Подготовлено сервисом TG-Monitoring по вашему поисковому запросу. Ссылка действует
              ограниченное время.
            </p>
            <ul className="mention-list samples-page__list">
              {data.items.map((item, index) => {
                const published = formatPublished(item.published_at);
                return (
                  <li key={`${item.url ?? item.text}-${index}`} className="mention-card">
                    <p className="mention-card__source">{item.source}</p>
                    {published ? <p className="sample-teaser-card__date">{published}</p> : null}
                    {item.title ? (
                      <h3>
                        <HighlightedText text={item.title} query={data.query} />
                      </h3>
                    ) : null}
                    <p>
                      <HighlightedText text={item.text} query={data.query} />
                    </p>
                    {item.url ? (
                      <a href={item.url} target="_blank" rel="noreferrer">
                        Открыть источник
                      </a>
                    ) : null}
                  </li>
                );
              })}
            </ul>
            {data.expires_note ? <p className="samples-page__expires">{data.expires_note}</p> : null}
          </>
        )}
      </div>
    </section>
  );
}
