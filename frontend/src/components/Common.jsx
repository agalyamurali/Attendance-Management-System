export function Loader({ label = "Loading..." }) {
  return <div className="loader">{label}</div>;
}

export function EmptyState({ message = "No data found." }) {
  return <div className="empty-state">{message}</div>;
}

export function ErrorMessage({ message }) {
  if (!message) return null;
  return <div className="error-message">{message}</div>;
}

export function SuccessMessage({ message }) {
  if (!message) return null;
  return <div className="success-message">{message}</div>;
}

/** ACTIVE/INACTIVE or PRESENT/ABSENT/etc rendered as a colored pill. */
export function StatusBadge({ status }) {
  return <span className={`badge badge-${status?.toLowerCase()}`}>{status}</span>;
}

/** Simple prev/next pagination — enough for this app's scale. */
export function Pagination({ page, pageSize, total, onPageChange }) {
  const totalPages = Math.max(Math.ceil(total / pageSize), 1);

  return (
    <div className="pagination">
      <button
        className="btn btn-secondary"
        disabled={page <= 1}
        onClick={() => onPageChange(page - 1)}
      >
        Previous
      </button>
      <span>
        Page {page} of {totalPages} ({total} total)
      </span>
      <button
        className="btn btn-secondary"
        disabled={page >= totalPages}
        onClick={() => onPageChange(page + 1)}
      >
        Next
      </button>
    </div>
  );
}
