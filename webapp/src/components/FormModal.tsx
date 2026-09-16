import { type FormEvent, useEffect, useRef, useState } from "react";

export type SelectOption = { value: string; label: string };

export type Field =
  | { kind: "text" | "email"; name: string; label: string; placeholder?: string }
  | {
      kind: "number";
      name: string;
      label: string;
      placeholder?: string;
      min?: string;
      step?: string;
    }
  | { kind: "datetime"; name: string; label: string; defaultValue: string }
  | {
      kind: "select";
      name: string;
      label: string;
      placeholder: string;
      options: SelectOption[];
      defaultValue?: string;
    };

function FieldInput({ field, focus }: { field: Field; focus: boolean }) {
  switch (field.kind) {
    case "select": {
      const selected =
        field.defaultValue && field.options.some((option) => option.value === field.defaultValue)
          ? field.defaultValue
          : "";
      return (
        <select name={field.name} defaultValue={selected} required autoFocus={focus}>
          <option value="" disabled>
            {field.placeholder}
          </option>
          {field.options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );
    }
    case "datetime":
      return (
        <input
          type="datetime-local"
          name={field.name}
          defaultValue={field.defaultValue}
          required
          autoFocus={focus}
        />
      );
    case "number":
      return (
        <input
          type="number"
          name={field.name}
          placeholder={field.placeholder}
          min={field.min}
          step={field.step}
          required
          autoFocus={focus}
        />
      );
    default:
      return (
        <input
          type={field.kind}
          name={field.name}
          placeholder={field.placeholder}
          required
          autoFocus={focus}
        />
      );
  }
}

export function FormModal({
  title,
  description,
  fields,
  submitLabel,
  onSubmit,
  onClose,
}: {
  title: string;
  description?: string;
  fields: Field[];
  submitLabel: string;
  onSubmit: (data: FormData) => Promise<void>;
  onClose: () => void;
}) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    dialogRef.current?.showModal();
  }, []);

  // A required dropdown with nothing to choose from means a prerequisite is missing.
  const blocked = fields.find(
    (field) => field.kind === "select" && field.options.length === 0,
  );

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    setError(null);
    setBusy(true);
    try {
      await onSubmit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save this record.");
      setBusy(false);
    }
  }

  function requestClose() {
    if (!busy) onClose();
  }

  return (
    <dialog
      ref={dialogRef}
      className="modal"
      onCancel={(event) => {
        event.preventDefault();
        requestClose();
      }}
      onClick={(event) => {
        if (event.target === dialogRef.current) requestClose();
      }}
    >
      <form className="modal__body" onSubmit={(event) => void handleSubmit(event)}>
        <header className="modal__head">
          <h2>{title}</h2>
          <button
            type="button"
            className="modal__close"
            onClick={requestClose}
            disabled={busy}
            aria-label="Close"
          >
            ×
          </button>
        </header>
        {description && <p className="hint">{description}</p>}
        {blocked && (
          <p className="banner">
            Add at least one {blocked.label.toLowerCase()} before creating this.
          </p>
        )}
        {error && <p className="banner error">{error}</p>}
        {fields.map((field, index) => (
          <label key={field.name}>
            {field.label}
            <FieldInput field={field} focus={index === 0} />
          </label>
        ))}
        <div className="modal__actions">
          <button type="button" className="ghost" onClick={requestClose} disabled={busy}>
            Cancel
          </button>
          <button type="submit" className="primary" disabled={busy || Boolean(blocked)}>
            {busy ? "Saving…" : submitLabel}
          </button>
        </div>
      </form>
    </dialog>
  );
}
