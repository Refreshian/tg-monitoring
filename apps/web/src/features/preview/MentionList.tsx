import { HighlightedText } from "@/components/HighlightedText";
import type { PreviewResponse } from "@/types/preview";

type MentionListProps = {
  result: PreviewResponse;
};

export function MentionList({ result }: MentionListProps) {
  return (
    <section className="mention-list">
      {result.items.length === 0 ? (
        <p>Не найдено упоминаний по введенному запросу</p>
      ) : (
        <>
          <h2>Последние найденные упоминания:</h2>
          <ul>
            {result.items.map((item, index) => (
              <li key={`${item.url ?? item.text}-${index}`} className="mention-card">
                <p className="mention-card__source">{item.source}</p>
                {item.title && (
                  <h3>
                    <HighlightedText text={item.title} query={result.query} />
                  </h3>
                )}
                <p>
                  <HighlightedText text={item.text} query={result.query} />
                </p>
                {item.url && (
                  <a href={item.url} target="_blank" rel="noreferrer">
                    Открыть источник
                  </a>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  );
}
