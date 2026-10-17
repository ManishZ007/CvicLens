"use client";
import { useEffect, useState } from "react";
export default function ResolutionNotes({ complaintId, note, onChange, disabled }: {
  complaintId: number; note: string; onChange: (value: string) => void; disabled: boolean;
}) {
  const [photo, setPhoto] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [savedUrl, setSavedUrl] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => () => { if (preview) URL.revokeObjectURL(preview); }, [preview]);
  async function upload() {
    if (!photo || busy) return;
    setBusy(true); setError("");
    try {
      const csrf = await fetch("/api/complaints/csrf/", { credentials: "include", cache: "no-store" });
      if (!csrf.ok) throw new Error("Could not prepare upload.");
      const { csrfToken } = await csrf.json();
      const body = new FormData(); body.set("photo", photo);
      const response = await fetch(`/api/complaints/${complaintId}/resolution-photo/`, {
        method: "POST", credentials: "include", headers: { "X-CSRFToken": csrfToken }, body,
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Upload failed.");
      setSavedUrl(data.url); setPhoto(null); setPreview("");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Upload failed."); }
    finally { setBusy(false); }
  }
  return <section className="space-y-3 rounded-xl border p-3">
    <label className="block">Resolution note
      <textarea value={note} disabled={disabled || busy} maxLength={1000} rows={4}
        onChange={event => onChange(event.target.value)} className="mt-2 w-full rounded border p-2" />
    </label>
    <label className="block">Resolution photo (required)
      <input type="file" accept="image/jpeg,image/png,image/webp" disabled={disabled || busy}
        onChange={event => {
          const file = event.target.files?.[0]; event.target.value = "";
          if (!file) return;
          if (!["image/jpeg", "image/png", "image/webp"].includes(file.type) || !file.size || file.size > 5 * 1024 * 1024) {
            setError("Choose a valid JPG, PNG or WebP up to 5 MB."); return;
          }
          setError(""); setPhoto(file); setPreview(URL.createObjectURL(file));
        }} className="mt-2 block w-full" />
    </label>
    {preview && <>
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={preview} alt="Resolution evidence preview" className="h-48 w-full object-contain" />
      <button type="button" disabled={busy || disabled} onClick={() => { setPhoto(null); setPreview(""); }} className="rounded border p-2">Remove selection</button>
    </>}
    <button type="button" disabled={!photo || busy || disabled} onClick={upload} className="rounded border p-2">{busy ? "Uploading…" : "Upload evidence"}</button>
    {savedUrl && <p role="status">Photo saved. <a href={savedUrl} className="underline">View saved evidence</a></p>}
    <p className="text-sm">Upload the photo first, then mark resolved to save the note and complete this work cycle.</p>
    {error && <p role="alert" className="text-red-700">{error}</p>}
  </section>;
}
