export type AccessRequestPayload = {
  contact_name: string;
  contact_phone: string;
  monitoring_object: string;
  contact_email?: string;
  query?: string;
  sample_token?: string;
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
