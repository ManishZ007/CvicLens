"use client";
import { useEffect, useState } from "react";
export type Draft = { text: string; category: string; latitude: string; longitude: string; language: "en" | "hi" | "mr" };

export default function ReportDraft({ value, onRestore }: { value: Draft; onRestore: (draft: Draft) => void }) {
  const [key, setKey] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    async function identify() {
      try {
        const response = await fetch("/api/users/me/", { credentials: "include", cache: "no-store", signal: controller.signal });
        if (!response.ok) return;
        const user = await response.json();
        if (!controller.signal.aborted) setKey(`civiclens-draft:${user.id}`);
      } catch { /* Draft access waits for an authenticated session. */ }
    }
    void identify();
    return () => controller.abort();
  }, []);

  function act(action: "save" | "restore" | "clear") {
    if (!key) return;
    try {
      if (action === "save") {
        localStorage.setItem(key, JSON.stringify({ ...value, savedAt: Date.now() }));
        setMessage("Text and location saved on this device. Photos and audio are not saved.");
      } else if (action === "clear") {
        localStorage.removeItem(key); setMessage("Saved draft cleared.");
      } else {
        const saved = localStorage.getItem(key);
        if (!saved) { setMessage("No saved draft for this account."); return; }
        const draft = JSON.parse(saved);
        if (!draft || typeof draft !== "object" ||
            !["text", "category", "latitude", "longitude"].every(field => typeof draft[field] === "string") ||
            draft.text.length > 5000 || !["en", "hi", "mr"].includes(draft.language) ||
            !["", "pothole", "garbage", "water", "light", "drain", "other"].includes(draft.category)) {
          throw new Error("Saved draft is invalid. Clear it and save a new one.");
        }
        onRestore(draft); setMessage("Draft restored. Check the text, location and attachments before submitting.");
      }
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Browser storage is unavailable."); }
  }
  return <section className="space-y-2 rounded-xl border p-3">
    <p className="text-sm">Optional device draft. Includes your description and coordinates; avoid shared computers.
      Restore replaces the current text and location. Nothing is submitted automatically.</p>
    <div className="flex flex-wrap gap-2">
      <button type="button" disabled={!key} onClick={() => act("save")} className="rounded border p-2">Save draft</button>
      <button type="button" disabled={!key} onClick={() => act("restore")} className="rounded border p-2">Restore draft</button>
      <button type="button" disabled={!key} onClick={() => act("clear")} className="rounded border p-2">Clear saved draft</button>
    </div>
    {!key && <p className="text-sm">Sign in and connect once to enable account-specific drafts.</p>}
    {message && <p role="status" className="text-sm">{message}</p>}
  </section>;
}
