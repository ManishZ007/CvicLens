"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

type Report = {
  id: number;
  description: string;
  category: string;
  status: string;
  priority: string;
  media: { id: number; url: string }[];
  department_id: number | null;
ward_id: number | null;
department: string | null;
ward: string | null;
assigned_worker: string | null;
};

type Worker = {
  id: number;
  name: string;
  department_id: number;
  ward_id: number;
};
const nextStatus: Record<string, string> = {
  submitted: "verified",
  verified: "assigned",
  assigned: "in_progress",
  in_progress: "resolved",
};

export default function OfficerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [report, setReport] = useState<Report | null>(null);
  const [note, setNote] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [workers, setWorkers] = useState<Worker[]>([]);
const [workerId, setWorkerId] = useState("");
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setReport(null);
      setError("");

      try {
        const access = await fetch("/api/complaints/?scope=officer", {
          credentials: "include",
          cache: "no-store",
          signal: controller.signal,
        });

        if (access.status === 401) {
          router.replace("/login");
          return;
        }

        if (!access.ok) {
  throw new Error("Officer access unavailable.");
}

const optionsResponse = await fetch(
  "/api/complaints/routing-options/",
  {
    credentials: "include",
    cache: "no-store",
    signal: controller.signal,
  },
);

if (!optionsResponse.ok) {
  throw new Error("Unable to load workers.");
}

const options = await optionsResponse.json();

if (!controller.signal.aborted) {
  setWorkers(options.workers);
  setWorkerId("");
}

const response = await fetch(`/api/complaints/${id}/`, {
          credentials: "include",
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Unable to load this complaint.");
        }

        const data = await response.json();

        if (!controller.signal.aborted) {
          setReport(data);
        }
      } catch (reason) {
        if (!controller.signal.aborted) {
          setError(
            reason instanceof Error ? reason.message : "Request failed.",
          );
        }
      }
    }

    void load();

    return () => controller.abort();
  }, [id, reload, router]);

  async function update() {
    if (!report || busy) return;

    setBusy(true);
    setError("");

    try {
      const tokenResponse = await fetch("/api/complaints/csrf/", {
        credentials: "include",
        cache: "no-store",
      });

      if (!tokenResponse.ok) {
        throw new Error("Unable to prepare update.");
      }

      const { csrfToken } = await tokenResponse.json();

     const response = await fetch(`/api/complaints/${id}/status/`, {
  method: "PATCH",
  credentials: "include",
  headers: {
    "Content-Type": "application/json",
    "X-CSRFToken": csrfToken,
  },
  body: JSON.stringify({
    expected_status: report.status,
    status: nextStatus[report.status],
    note,
    worker_id: workerId ? Number(workerId) : null,
  }),
});

      if (response.status === 409) {
        throw new Error(
          "Another officer changed this report. Refresh first.",
        );
      }

      if (!response.ok) {
        throw new Error("Update failed. Check access and retry.");
      }

      setReport(await response.json());
      setNote("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Update failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#EDF0F4] p-6 text-[#18202E]">
      <section className="mx-auto max-w-2xl space-y-4 rounded-xl bg-white p-6">
        <h1 className="text-2xl font-bold">Complaint #{id}</h1>

        {error && (
          <p role="alert" className="text-red-700">
            {error}
          </p>
        )}

        {!report && !error && <p role="status">Loading…</p>}

        {report && (
          <>
            <p className="whitespace-pre-wrap">{report.description}</p>

            <p>
              {report.category} · {report.priority}
            </p>

            <p>
              Status: {report.status.replaceAll("_", " ")}
            </p>
            <p>
  Department: {report.department || "Pending"}
</p>

<p>
  Ward: {report.ward || "Manual routing required"}
</p>

<p>
  Worker: {report.assigned_worker || "Not assigned"}
</p>

            {report.media.map((photo) => (
              <a
                key={photo.id}
                href={photo.url}
                className="block text-blue-800 underline"
              >
                View photo #{photo.id}
              </a>
            ))}

            {nextStatus[report.status] ? (
  <>
    {report.status === "verified" && (
      <label className="block">
        Assign a worker

        <select
          value={workerId}
          disabled={busy}
          onChange={(event) => setWorkerId(event.target.value)}
          className="mt-2 w-full rounded-lg border bg-white p-3"
        >
          <option value="">Choose a worker</option>

          {workers
            .filter(
              (worker) =>
                worker.department_id === report.department_id &&
                worker.ward_id === report.ward_id,
            )
            .map((worker) => (
              <option key={worker.id} value={worker.id}>
                {worker.name}
              </option>
            ))}
        </select>

        <span className="text-sm text-gray-600">
          Only active workers matching this department and ward are listed.
        </span>
      </label>
    )}

    <label className="block">
      Officer note
                  <textarea
                    value={note}
                    disabled={busy}
                    onChange={(event) => setNote(event.target.value)}
                    maxLength={1000}
                    className="mt-2 w-full rounded-lg border p-3"
                  />
                </label>

                <button
                  type="button"
                  disabled={
  busy ||
  (report.status === "verified" && !workerId)
}
                  onClick={update}
                  className="rounded-lg bg-[#1B4F9C] p-3 text-white disabled:opacity-50"
                >
                  {busy
                    ? "Updating…"
                    : `Mark ${nextStatus[report.status].replaceAll("_", " ")}`}
                </button>
              </>
            ) : (
              <p>This complaint is resolved.</p>
            )}
          </>
        )}

        <div className="flex gap-4">
          <button
            type="button"
            disabled={busy}
            onClick={() => setReload((value) => value + 1)}
            className="rounded-lg border p-2"
          >
            Refresh
          </button>

          <Link
            href="/officer"
            className="p-2 text-blue-800 underline"
          >
            Back to console
          </Link>
        </div>
      </section>
    </main>
  );
}