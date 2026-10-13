
"use client";

import { useEffect, useState } from "react";

export default function ResolutionNotes({
  note,
  onChange,
  disabled,
}: {
  note: string;
  onChange: (value: string) => void;
  disabled: boolean;
}) {
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");

  useEffect(
    () => () => {
      if (preview) URL.revokeObjectURL(preview);
    },
    [preview],
  );

  return (
    <section className="space-y-3 rounded-xl border p-3">
      <label className="block">
        Resolution note

        <textarea
          value={note}
          disabled={disabled}
          maxLength={1000}
          rows={4}
          onChange={(event) => onChange(event.target.value)}
          placeholder="Explain what was repaired and the work completed."
          className="mt-2 w-full rounded border p-2"
        />
      </label>

      <p className="text-sm">
        The note is saved when you mark the complaint resolved.
      </p>

      <label className="block">
        Resolution photo — preview only

        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          disabled={disabled}
          onChange={(event) => {
            const file = event.target.files?.[0];

            // Allow the same file to be selected again.
            event.target.value = "";

            if (!file) return;

            if (
              !["image/jpeg", "image/png", "image/webp"].includes(
                file.type,
              ) ||
              !file.size ||
              file.size > 5 * 1024 * 1024
            ) {
              setError("Choose a JPG, PNG or WebP image up to 5 MB.");
              return;
            }

            setError("");
            setPreview(URL.createObjectURL(file));
          }}
          className="mt-2 block w-full"
        />
      </label>

      <p className="text-sm text-gray-600">
        This preview is not uploaded or saved yet.
      </p>

      {preview && (
        <>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={preview}
            alt="Resolution photo preview"
            className="h-48 w-full object-contain"
          />

          <button
            type="button"
            disabled={disabled}
            onClick={() => {
              setPreview("");
              setError("");
            }}
            className="rounded border p-2"
          >
            Remove preview
          </button>
        </>
      )}

      {error && (
        <p role="alert" className="text-red-700">
          {error}
        </p>
      )}
    </section>
  );
}
