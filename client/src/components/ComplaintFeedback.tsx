"use client";
import { useEffect, useState } from "react";
export default function ComplaintFeedback({ id, onReopened }: { id: number; onReopened: () => void }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await fetch(`/api/complaints/${id}/feedback/`, { credentials: "include", cache: "no-store", signal: controller.signal });
        if (!response.ok) throw new Error("Could not load saved feedback. Refresh to retry.");
        const { feedback } = await response.json();
        if (feedback && !controller.signal.aborted) { setRating(feedback.rating); setComment(feedback.comment); }
      } catch (reason) { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Request failed."); }
      finally { if (!controller.signal.aborted) setLoading(false); }
    }
    void load(); return () => controller.abort();
  }, [id]);

  async function send(action: "feedback" | "reopen") {
    setBusy(true); setError(""); setMessage("");
    try {
      const csrf = await fetch("/api/complaints/csrf/", { credentials: "include", cache: "no-store" });
      if (!csrf.ok) throw new Error("Could not prepare update.");
      const { csrfToken } = await csrf.json();
      const response = await fetch(`/api/complaints/${id}/${action}/`, {
        method: "POST", credentials: "include", headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
        body: JSON.stringify(action === "feedback" ? { rating, comment } : { reason }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Update failed.");
      if (action === "reopen") onReopened(); else setMessage("Feedback saved.");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Update failed."); }
    finally { setBusy(false); }
  }
  return <section className="space-y-3 rounded-xl border p-3">
    <h2 className="font-semibold">Was the issue fixed?</h2>
    {loading && <p>Loading feedback…</p>}
    <fieldset disabled={busy || loading} className="space-y-3">
      <label className="block">Rating
        <select value={rating} onChange={event => setRating(Number(event.target.value))} className="ml-2 border p-2">
          {[1,2,3,4,5].map(value => <option key={value} value={value}>{value} / 5</option>)}
        </select>
      </label>
      <label className="block">Feedback
        <textarea value={comment} maxLength={1000} onChange={event => setComment(event.target.value)} className="block w-full border p-2" />
      </label>
      <button type="button" onClick={() => send("feedback")} className="rounded border p-2">Save feedback</button>
      <label className="block">Issue still unresolved? Explain why
        <textarea value={reason} maxLength={1000} onChange={event => setReason(event.target.value)} className="block w-full border p-2" />
      </label>
      <button type="button" disabled={!reason.trim()} onClick={() => send("reopen")} className="rounded border p-2">Reopen for reassignment</button>
    </fieldset>
    {error && <p role="alert" className="text-red-700">{error}</p>}
    {message && <p role="status">{message}</p>}
  </section>;
}
