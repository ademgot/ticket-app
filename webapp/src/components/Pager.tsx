import { PAGE_SIZE } from "../api/paging";

export function Pager({
  page,
  total,
  onPage,
}: {
  page: number;
  total: number;
  onPage: (page: number) => void;
}) {
  const pageCount = Math.max(1, Math.ceil(total / PAGE_SIZE));
  if (total <= PAGE_SIZE) {
    return null;
  }
  const start = (page - 1) * PAGE_SIZE + 1;
  const end = Math.min(page * PAGE_SIZE, total);

  return (
    <nav className="pager" aria-label="Pages">
      <button
        type="button"
        className="ghost compact"
        disabled={page <= 1}
        onClick={() => onPage(page - 1)}
      >
        Previous
      </button>
      <span>
        {start}–{end} of {total}
      </span>
      <button
        type="button"
        className="ghost compact"
        disabled={page >= pageCount}
        onClick={() => onPage(page + 1)}
      >
        Next
      </button>
    </nav>
  );
}
