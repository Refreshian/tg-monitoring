import { FormEvent } from "react";

type PreviewSearchFormProps = {
  query: string;
  loading: boolean;
  onQueryChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
};

export function PreviewSearchForm({
  query,
  loading,
  onQueryChange,
  onSubmit,
}: PreviewSearchFormProps) {
  return (
    <form className="search-form" onSubmit={onSubmit}>
      <label htmlFor="query">Поисковый запрос</label>
      <textarea
        id="query"
        value={query}
        onChange={(event) => onQueryChange(event.target.value)}
        placeholder='Например: "ООО Ромашка" OR "Иванов Иван"'
        rows={4}
        required
      />
      <button className="button button--primary" type="submit" disabled={loading}>
        {loading ? "Оцениваем объём..." : "Оценить объём и стоимость"}
      </button>
    </form>
  );
}
