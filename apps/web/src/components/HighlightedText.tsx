import { extractSearchTerms, highlightText } from "@/lib/highlightSearchTerms";

type HighlightedTextProps = {
  text: string;
  query: string;
};

export function HighlightedText({ text, query }: HighlightedTextProps) {
  const terms = extractSearchTerms(query);
  const parts = highlightText(text, terms);

  return (
    <>
      {parts.map((part, index) =>
        typeof part === "string" ? (
          <span key={index}>{part}</span>
        ) : (
          <mark key={index} className="search-hit">
            {part.mark}
          </mark>
        ),
      )}
    </>
  );
}
