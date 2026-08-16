type QueryRewriteNoticeProps = {
  originalQuery: string;
  query: string;
  note?: string | null;
};

export function QueryRewriteNotice({ originalQuery, query, note }: QueryRewriteNoticeProps) {
  return (
    <section className="query-rewrite" aria-live="polite">
      <h2 className="query-rewrite__title">Запрос уточнён для поиска</h2>
      <p className="query-rewrite__line">
        <span className="query-rewrite__label">Было:</span> {originalQuery}
      </p>
      <p className="query-rewrite__line">
        <span className="query-rewrite__label">Стало:</span> <code>{query}</code>
      </p>
      {note ? <p className="query-rewrite__note">{note}</p> : null}
    </section>
  );
}
