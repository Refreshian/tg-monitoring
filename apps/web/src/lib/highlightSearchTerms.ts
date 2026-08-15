/**
 * Extract searchable phrases/words from a Brand Analytics-style query.
 * Supports quoted phrases, bare tokens; skips AND/OR/NOT and proximity suffixes.
 */
export function extractSearchTerms(query: string): string[] {
  const terms: string[] = [];
  const seen = new Set<string>();

  const quoted = [...query.matchAll(/"([^"]+)"(?:~\d+)?/g)];
  for (const match of quoted) {
    addTerm(match[1], terms, seen);
  }

  const withoutQuotes = query.replace(/"[^"]+"(?:~\d+)?/g, " ");
  for (const token of withoutQuotes.split(/[\s,|]+/)) {
    const cleaned = token.replace(/[()]/g, "").trim();
    if (!cleaned) continue;
    if (/^(AND|OR|NOT|NEAR)$/i.test(cleaned)) continue;
    if (/^~\d+$/.test(cleaned)) continue;
    addTerm(cleaned, terms, seen);
  }

  // Longer phrases first so "Russian Creative Week" wins over "Russian"
  return terms.sort((a, b) => b.length - a.length);
}

function addTerm(raw: string, terms: string[], seen: Set<string>) {
  const term = raw.trim();
  if (term.length < 2) return;
  const key = term.toLocaleLowerCase("ru-RU");
  if (seen.has(key)) return;
  seen.add(key);
  terms.push(term);
}

export function highlightText(text: string, terms: string[]): Array<string | { mark: string }> {
  if (!text || terms.length === 0) return [text];

  const escaped = terms.map((term) =>
    term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"),
  );
  const pattern = new RegExp(`(${escaped.join("|")})`, "giu");
  const parts: Array<string | { mark: string }> = [];
  let lastIndex = 0;

  for (const match of text.matchAll(pattern)) {
    const index = match.index ?? 0;
    if (index > lastIndex) {
      parts.push(text.slice(lastIndex, index));
    }
    parts.push({ mark: match[0] });
    lastIndex = index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : [text];
}
