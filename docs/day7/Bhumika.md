# Day 7 — Bhumika: notification inbox

Naman's Day 7 API must be merged for live data. Create `client/src/app/notifications/page.tsx`:

```tsx
"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import AppShell from "@/components/AppShell";

type Alert = {
  id: number; complaint_id: number; message: string;
  is_read: boolean; created_at: string;
};
type Inbox = { results: Alert[]; unread_count: number; page: number; pages: number };

export default function NotificationsPage() {
  const [data, setData] = useState<Inbox | null>(null);
  const [page, setPage] = useState(1);
  const [reload, setReload] = useState(0);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      setLoading(true);
      setError("");
      try {
        const response = await fetch(`/api/complaints/notifications/?page=${page}`, {
          credentials: "include", cache: "no-store", signal: controller.signal,
        });
        if (response.status === 401) throw new Error("Sign in to see notifications.");
        if (!response.ok) throw new Error("Could not load notifications. Retry after the API is available.");
        const result: Inbox = await response.json();
        if (!controller.signal.aborted) setData(result);
      } catch (reason) {
        if (!controller.signal.aborted)
          setError(reason instanceof Error ? reason.message : "Could not load notifications.");
      } finally { if (!controller.signal.aborted) setLoading(false); }
    }
    void load();
    return () => controller.abort();
  }, [page, reload]);

  async function read(id: number) {
    setBusy(true);
    setError("");
    try {
      const csrf = await fetch("/api/complaints/csrf/", { credentials: "include", cache: "no-store" });
      if (!csrf.ok) throw new Error("Could not prepare update.");
      const { csrfToken } = await csrf.json();
      const response = await fetch(`/api/complaints/notifications/${id}/read/`, {
        method: "PATCH", credentials: "include", headers: { "X-CSRFToken": csrfToken },
      });
      if (!response.ok) throw new Error("Could not mark this notification as read.");
      setReload(value => value + 1);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Update failed.");
    } finally { setBusy(false); }
  }

  return <AppShell title="Notifications">
    <div className="space-y-4">
      {error && <p role="alert" className="text-red-700">{error}</p>}
      {loading && <p role="status">Loading…</p>}
      <button type="button" disabled={busy || loading} onClick={() => setReload(value => value + 1)}
        className="rounded border p-2">Refresh</button>
      {!loading && !error && data && <>
        <p aria-live="polite">Unread: {data.unread_count}</p>
        {data.results.length === 0 && <p>No notifications yet.</p>}
        {data.results.map(item => <article key={item.id}
          className={`space-y-2 rounded-xl border p-3 ${item.is_read ? "bg-white" : "bg-blue-50"}`}>
          <p>{!item.is_read && <strong>New: </strong>}{item.message}</p>
          <time className="block text-sm" dateTime={item.created_at}>
            {new Date(item.created_at).toLocaleString()}
          </time>
          <Link href={`/my-reports/${item.complaint_id}`} className="block text-blue-800 underline">
            Open complaint #{item.complaint_id}
          </Link>
          {!item.is_read && <button type="button" disabled={busy}
            onClick={() => read(item.id)} className="rounded border p-2">Mark as read</button>}
        </article>)}
        <div className="flex items-center justify-between">
          <button type="button" disabled={busy || data.page <= 1}
            onClick={() => setPage(data.page - 1)}>Previous</button>
          <span>{data.page} / {data.pages}</span>
          <button type="button" disabled={busy || data.page >= data.pages}
            onClick={() => setPage(data.page + 1)}>Next</button>
        </div>
      </>}
    </div>
  </AppShell>;
}
```

In `client/src/components/AppShell.tsx`, insert inside the existing `<nav>`:

```tsx
<Link href="/notifications">
  {{ en: "Notifications", hi: "सूचनाएँ", mr: "सूचना" }[language]}
</Link>
```

Check: officer changes status → citizen sees alert; mark read → refresh stays read;
another citizen cannot see the alert; API failure shows error; pagination works.
Run `npm run lint` and `npx tsc --noEmit` from `client`.

Commit: `feat(citizen): add notification inbox and unread count`
