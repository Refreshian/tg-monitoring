import type { PreviewResponse } from "@/types/preview";

type MentionListProps = {
  result: PreviewResponse;
};

export function MentionList({ result }: MentionListProps) {
  return (
    <section className="mention-list">
      <h2>Найдено: {result.total}</h2>
      {result.items.length === 0 ? (
        <p>По запросу пока ничего не найдено.</p>
      ) : (
        <ul>
          {result.items.map((item, index) => (
            <li key={`${item.url ?? item.text}-${index}`} className="mention-card">
              <p className="mention-card__source">{item.source}</p>
              {item.title && <h3>{item.title}</h3>}
              <p>{item.text}</p>
              {item.url && (
                <a href={item.url} target="_blank" rel="noreferrer">
                  Открыть источник
                </a>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
