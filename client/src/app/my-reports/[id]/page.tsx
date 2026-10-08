"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import StatusTimeline from "@/components/StatusTimeline";

type Detail = {
  id: number;
  description: string;
  category: string;
  status: string;
  priority: string;
  media: { id: number; url: string }[];
  history: { status: string; note: string; created_at: string }[];
};

export default function ReportDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [report, setReport] = useState<Detail | null>(null);
  const [error, setError] = useState("");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setReport(null);
      setError("");

      try {
        const response = await fetch(`/api/complaints/${id}/`, {
          credentials: "include",
          cache: "no-store",
          signal: controller.signal,
        });

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (!response.ok) {
          throw new Error("Report unavailable.");
        }

        setReport(await response.json());
      } catch {
        if (!controller.signal.aborted) {
          setError("Unable to load this report.");
        }
      }
    }

    void load();

    return () => controller.abort();
  }, [id, retry, router]);

  return (
    <AppShell title={`Report #${id}`}>
      {error ? (
        <p role="alert">{error}</p>
      ) : !report ? (
        <p role="status">Loading…</p>
      ) : (
        <div className="space-y-4">
          <p className="whitespace-pre-wrap">{report.description}</p>

          <p>
            {report.category} · {report.priority}
          </p>

          <p>Status: {report.status.replaceAll("_", " ")}</p>

          {report.media.map((photo) => (
            <a
              key={photo.id}
              href={photo.url}
              className="block text-blue-800 underline"
            >
              View attached photo #{photo.id}
            </a>
          ))}

          <StatusTimeline
            status={report.status}
            history={report.history}
          />

          <button
            type="button"
            onClick={() => setRetry((value) => value + 1)}
            className="rounded-lg border p-2"
          >
            Refresh status
          </button>
        </div>
      )}
    </AppShell>
  );
}