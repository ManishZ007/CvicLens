"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";

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
  }, [id, router]);

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

          <h2 className="font-semibold">History</h2>

          <ol className="space-y-3">
            {report.history.map((entry, index) => (
              <li
                key={`${entry.created_at}-${index}`}
                className="border-l-2 pl-3"
              >
                <p>{entry.status.replaceAll("_", " ")}</p>

                <p className="text-sm">{entry.note}</p>

                <time className="text-sm text-gray-500">
                  {new Date(entry.created_at).toLocaleString()}
                </time>
              </li>
            ))}
          </ol>
        </div>
      )}
    </AppShell>
  );
}