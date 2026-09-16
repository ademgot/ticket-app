const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

type ValidationIssue = { loc?: unknown[]; msg?: string };

// FastAPI reports failures as {"detail": string} or, for validation, a list of issues.
function readError(response: Response, body: string): string {
  try {
    const detail = (JSON.parse(body) as { detail?: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((issue: ValidationIssue) => {
          const field = issue.loc?.at(-1);
          return field ? `${String(field)}: ${issue.msg}` : issue.msg;
        })
        .filter(Boolean)
        .join("; ");
    }
  } catch {
    // Not a JSON body, fall through to the raw text.
  }
  return body || `${response.status} ${response.statusText}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  const text = await response.text();
  if (!response.ok) {
    throw new Error(readError(response, text));
  }
  if (!text) {
    return undefined as T;
  }
  return JSON.parse(text) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
