import type { MentionTeaser } from "@/types/preview";

type SampleTeasersProps = {
  teasers: MentionTeaser[];
};

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

export function SampleTeasers({ teasers }: SampleTeasersProps) {
  if (teasers.length === 0) {
    return null;
  }

  return (
    <section className="sample-teasers">
      <h2 className="sample-teasers__title">Найденные упоминания (без текста на сайте)</h2>
      <p className="sample-teasers__note">
        По вашему запросу есть сообщения в источниках — преимущественно VK, если он есть в
        выдаче. Тексты не показываем на открытой странице: ниже источник и ссылка. Полные
        примеры можно получить на email (10 сообщений).
      </p>
      <ul className="sample-teasers__list">
        {teasers.map((teaser, index) => {
          const published = formatPublished(teaser.published_at);
          return (
            <li key={`${teaser.source}-${index}`} className="sample-teaser-card">
              <p className="sample-teaser-card__source">{teaser.source}</p>
              {published ? <p className="sample-teaser-card__date">{published}</p> : null}
              <p className="sample-teaser-card__hint">Упоминание найдено</p>
              {teaser.url ? (
                <a href={teaser.url} target="_blank" rel="noreferrer">
                  Открыть источник
                </a>
              ) : (
                <span className="sample-teaser-card__no-link">Ссылка на источник недоступна</span>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
