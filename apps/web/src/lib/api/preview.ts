import type {
  PreviewResponse,
  PreviewSamplesResponse,
  SendSamplesResponse,
} from "@/types/preview";

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

export async function sendPreviewSamples(
  sampleToken: string,
  email: string,
): Promise<SendSamplesResponse> {
  const response = await fetch("/api/v1/preview/send-samples", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sample_token: sampleToken, email }),
  });

  if (!response.ok) {
    throw new Error("Send samples failed");
  }

  return response.json() as Promise<SendSamplesResponse>;
}

export async function fetchPreviewSamples(token: string): Promise<PreviewSamplesResponse> {
  const response = await fetch(`/api/v1/preview/samples/${encodeURIComponent(token)}`);

  if (!response.ok) {
    throw new Error("Samples not found");
  }

  return response.json() as Promise<PreviewSamplesResponse>;
}
