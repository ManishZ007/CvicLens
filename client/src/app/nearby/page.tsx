"use client";
import { useRef, useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
type Nearby = { id: number; category: string; status: string; distance_metres: number };
export default function NearbyPage() {
  const [rows, setRows] = useState<Nearby[] | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [truncated, setTruncated] = useState(false);
  const alive = useRef(true);
  const request = useRef<AbortController | null>(null);
  useEffect(() => { alive.current = true; return () => { alive.current = false; request.current?.abort(); }; }, []);

  function load() {
    if (!navigator.geolocation) { setError("Location is unavailable in this browser."); return; }
    setBusy(true); setError(""); setRows(null);
    navigator.geolocation.getCurrentPosition(async ({ coords }) => {
      if (!alive.current) return;
      const controller = new AbortController(); request.current = controller;
      try {
        const query = new URLSearchParams({ latitude: String(coords.latitude), longitude: String(coords.longitude) });
        const response = await fetch(`/api/ai/nearby/?${query}`, { credentials: "include", cache: "no-store", signal: controller.signal });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Could not load nearby reports.");
        if (alive.current) { setRows(data.results); setTruncated(data.truncated); }
      } catch (reason) {
        if (alive.current && !controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Request failed.");
      } finally { if (alive.current) setBusy(false); }
    }, () => { if (alive.current) { setError("Allow location access and retry."); setBusy(false); } }, { timeout: 10000 });
  }
  return <AppShell title="Nearby issues">
    <div className="space-y-3">
      <p>Open reports within 2 km, submitted in the past 30 days.</p>
      <button type="button" disabled={busy} onClick={load} className="rounded border p-2">{busy ? "Finding reports…" : "Use my location"}</button>
      {error && <p role="alert" className="text-red-700">{error}</p>}
      {rows?.length === 0 && <p>No nearby reports found in the checked records.</p>}
      {rows?.map(row => <article key={row.id} className="rounded-xl border p-3">
        <p>#{row.id} · {row.category} · {row.distance_metres} m</p><p>{row.status.replaceAll("_", " ")}</p>
      </article>)}
      {truncated && <p>Showing a limited selection of nearby reports.</p>}
    </div>
  </AppShell>;
}
