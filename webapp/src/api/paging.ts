export const PAGE_SIZE = 50;

export function pageUrl(
  path: string,
  page: number,
  filters?: Record<string, string | undefined>,
): string {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(PAGE_SIZE),
  });
  Object.entries(filters ?? {}).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });
  return `${path}?${params.toString()}`;
}
