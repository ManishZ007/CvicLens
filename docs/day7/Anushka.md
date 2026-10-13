# Day 7 — Anushka: resolution form and photo preview

Today saves officer notes through the existing status API. Resolution photos are
**local previews only**; persistence/enforcement belongs to the later evidence task.
Keep the visible preview-only wording so officers are not told a photo was uploaded.

Create `client/src/components/ResolutionNotes.tsx`:

```tsx
"use client";
import { useEffect, useState } from "react";

export default function ResolutionNotes({ note, onChange, disabled }: {
  note: string; onChange: (value: string) => void; disabled: boolean;
}) {
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);

  return <section className="space-y-3 rounded-xl border p-3">
    <label className="block">Resolution note
      <textarea value={note} disabled={disabled} maxLength={1000} rows={4}
        onChange={event => onChange(event.target.value)}
        placeholder="Explain what was repaired and the work completed."
        className="mt-2 w-full rounded border p-2" />
    </label>
    <p className="text-sm">The note is saved when you mark the complaint resolved.</p>
    <label className="block">Resolution photo — preview only
      <input type="file" accept="image/jpeg,image/png,image/webp" disabled={disabled}
        onChange={event => {
          const file = event.target.files?.[0];
          event.target.value = "";
          if (!file) return;
          if (!["image/jpeg", "image/png", "image/webp"].includes(file.type) ||
              !file.size || file.size > 5 * 1024 * 1024) {
            setError("Choose a JPG, PNG or WebP image up to 5 MB.");
            return;
          }
          setError("");
          setPreview(URL.createObjectURL(file));
        }} className="mt-2 block w-full" />
    </label>
    <p className="text-sm text-gray-600">This preview is not uploaded or saved yet.</p>
    {preview && <>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={preview} alt="Resolution photo preview" className="h-48 w-full object-contain" />
      <button type="button" disabled={disabled} onClick={() => setPreview("")}
        className="rounded border p-2">Remove preview</button>
    </>}
    {error && <p role="alert" className="text-red-700">{error}</p>}
  </section>;
}
```

In `client/src/app/officer/[id]/page.tsx`, add:

```tsx
import ResolutionNotes from "@/components/ResolutionNotes";
```

Replace the existing **Officer note** label/textarea block with:

```tsx
{report.status === "in_progress" ? (
  <ResolutionNotes note={note} onChange={setNote} disabled={busy} />
) : (
  <label className="block">
    Officer note
    <textarea value={note} disabled={busy} maxLength={1000}
      onChange={event => setNote(event.target.value)}
      className="mt-2 w-full rounded-lg border p-3" />
  </label>
)}
```

Inside `update()`, immediately after `if (!report || busy) return;`, add:

```tsx
if (report.status === "in_progress" && !note.trim()) {
  setError("Add a resolution note before completing the complaint.");
  return;
}
```

This is UI guidance; server enforcement and saved resolution evidence are later work.
Check: worker assignment still works; notes appear in citizen timeline; invalid images
show errors; changing/removing preview works; no UI says the photo was saved.
Run `npm run lint` and `npx tsc --noEmit` from `client`.

Commit: `feat(officer): add resolution notes and local evidence preview`
