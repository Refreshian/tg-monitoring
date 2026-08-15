export type AccessRequestPayload = {
  query: string;
  contact_name: string;
  contact_email: string;
  contact_phone?: string;
  message?: string;
};

export async function createAccessRequest(payload: AccessRequestPayload): Promise<void> {
  const response = await fetch("/api/v1/access-requests", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error("Access request failed");
  }
}
