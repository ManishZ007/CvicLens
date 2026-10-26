"use client";
import { useEffect, useState } from "react";
import { csrfToken } from "@/lib/csrf";
type Option = { id: number; name: string };
export default function ManualRouting({ id, status, onSaved }: { id: number; status: string; onSaved: () => void }) {
  const [departments, setDepartments] = useState<Option[]>([]);
  const [wards, setWards] = useState<Option[]>([]);
  const [department, setDepartment] = useState("");
  const [ward, setWard] = useState("");
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    async function load() {
      try {
        const response = await fetch("/api/complaints/routing-options/", { credentials: "include", cache: "no-store", signal: controller.signal });
        if (!response.ok) throw new Error("Could not load routing options.");
        const data = await response.json();
        if (!controller.signal.aborted) { setDepartments(data.departments); setWards(data.wards); }
      } catch (reason) { if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Request failed."); }
    }
    void load(); return () => controller.abort();
  }, []);
  async function save() {
    setBusy(true); setError("");
    try {
      const response = await fetch(`/api/complaints/${id}/routing/`, {
        method: "PATCH", credentials: "include",
        headers: { "Content-Type": "application/json", "X-CSRFToken": await csrfToken() },
        body: JSON.stringify({ department_id: Number(department), ward_id: Number(ward), expected_status: status, note }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Routing update failed.");
      onSaved();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Routing update failed."); }
    finally { setBusy(false); }
  }
  return <details className="rounded-xl border p-3"><summary>Set department and ward manually</summary>
    <p className="my-2 text-sm">Use when automatic routing is unavailable. Demo wards are not official municipal boundaries.</p>
    <fieldset disabled={busy} className="space-y-2">
      <label className="block">Responsible department<select value={department} onChange={e => setDepartment(e.target.value)} className="block w-full border p-2">
        <option value="">Choose department</option>{departments.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
      <label className="block">Responsible ward<select value={ward} onChange={e => setWard(e.target.value)} className="block w-full border p-2">
        <option value="">Choose ward</option>{wards.map(item => <option key={item.id} value={item.id}>{item.name}</option>)}</select></label>
      <label className="block">Routing reason<textarea value={note} maxLength={1000} onChange={e => setNote(e.target.value)} className="block w-full border p-2" /></label>
      <button type="button" disabled={!department || !ward || !note.trim()} onClick={save} className="rounded border p-2">{busy ? "Saving…" : "Save routing"}</button>
    </fieldset>{error && <p role="alert" className="text-red-700">{error}</p>}
  </details>;
}
