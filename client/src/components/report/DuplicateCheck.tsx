"use client";
import { useEffect, useRef, useState } from "react";

type Match = { id: number; category: string; status: string; distance_metres: number; similarity: number };
export default function DuplicateCheck({ text, category, latitude, longitude }: {
  text: string; category: string; latitude: string; longitude: string;
}) {
  const [results, setResults] = useState<Match[] | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [truncated, setTruncated] = useState(false);
  const request = useRef<AbortController | null>(null);
  useEffect(() => () => request.current?.abort(), []);

  async function check() {
    setBusy(true); setError(""); setResults(null);
    const controller = new AbortController();
    request.current = controller;
    try {
      const csrf = await fetch("/api/complaints/csrf/", { credentials: "include", cache: "no-store", signal: controller.signal });
      if (!csrf.ok) throw new Error("Could not prepare duplicate check.");
      const { csrfToken } = await csrf.json();
      const response = await fetch("/api/ai/duplicates/", {
        method: "POST", credentials: "include", signal: controller.signal,
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify({ text, category: category || "other", latitude: Number(latitude), longitude: Number(longitude) }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Duplicate check failed.");
      if (!controller.signal.aborted) { setResults(data.results); setTruncated(data.truncated); }
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Duplicate check failed.");
    } finally { if (!controller.signal.aborted) setBusy(false); }
  }

  return <section className="space-y-2 rounded-xl border p-3">
    <button type="button" disabled={busy || !text.trim() || !latitude.trim() || !longitude.trim()}
      onClick={check} className="rounded border p-2">{busy ? "Checking…" : "Check similar nearby reports"}</button>
    <p className="text-sm">Checks matching words and category within 200 m, from the past 30 days.</p>
    {error && <p role="alert" className="text-red-700">{error} You can still submit.</p>}
    {results?.length === 0 && <p>No matching reports found in the checked records.</p>}
    {results?.map(item => <p key={item.id}>Possible duplicate #{item.id}: {item.category}, {item.distance_metres} m away, {item.status.replaceAll("_", " ")}</p>)}
    {truncated && <p>Only part of the nearby records could be checked.</p>}
    {results && <p className="text-sm">Suggestions only. Reports are not merged; submit if this is a separate issue.</p>}
  </section>;
}
