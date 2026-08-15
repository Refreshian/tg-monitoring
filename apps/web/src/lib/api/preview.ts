import type { PreviewResponse } from "@/types/preview";

export async function previewSearch(query: string): Promise<PreviewResponse> {
  const response = await fetch("/api/v1/preview/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    throw new Error("Preview request failed");
  }

  return response.json() as Promise<PreviewResponse>;
}
