"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import AppShell from "@/components/AppShell";
import StatusTimeline from "@/components/StatusTimeline";
import RoutingSummary, {
  type RoutingInfo,
} from "@/components/RoutingSummary";

type Detail = RoutingInfo & {
  id: number;
  description: string;
  category: string;
  status: string;
  priority: string;
  latitude: number | null;
  longitude: number | null;
  media: { id: number; url: string }[];
  history: {
    status: string;
    note: string;
    created_at: string;
  }[];
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
        const response = await fetch(
          `/api/complaints/${encodeURIComponent(id)}/`,
          {
            credentials: "include",
            cache: "no-store",
            signal: controller.signal,
          }
        );

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (response.status === 404) {
          throw new Error(
            "Report not found or unavailable to your account."
          );
        }

        if (!response.ok) {
          throw new Error("Unable to load this report.");
        }

        const data: Detail = await response.json();

        if (!controller.signal.aborted) {
          setReport(data);
        }
      } catch (reason) {
        if (!controller.signal.aborted) {
          setError(
            reason instanceof Error
              ? reason.message
              : "Request failed."
          );
        }
      }
    }

    void load();

    return () => controller.abort();
  }, [id, retry, router]);

  return (
    <AppShell title={`Report #${id}`}>
      {error ? (
        <div>
          <p role="alert">{error}</p>

          <button
            type="button"
            onClick={() => setRetry((previous) => previous + 1)}
            className="mt-2 rounded-lg border p-2"
          >
            Retry
          </button>
        </div>
      ) : !report ? (
        <p role="status">Loading report…</p>
      ) : (
        <div className="space-y-4">
          <p className="whitespace-pre-wrap break-words">
            {report.description}
          </p>

          <p>
            {report.category} · {report.priority}
          </p>

          <p>
            Status: {report.status.replaceAll("_", " ")}
          </p>

          {report.latitude !== null &&
            report.longitude !== null && (
              <p className="break-words text-sm">
                Location: {report.latitude}, {report.longitude}
              </p>
            )}

          {report.media.map((photo) => (
            <a
              key={photo.id}
              href={photo.url}
              className="block text-blue-800 underline"
            >
              View attached photo #{photo.id}
            </a>
          ))}

          <RoutingSummary report={report} />

          <StatusTimeline
            status={report.status}
            history={report.history}
          />

          <button
            type="button"
            onClick={() => setRetry((previous) => previous + 1)}
            className="rounded-lg border p-2"
          >
            Refresh status
          </button>
        </div>
      )}

      <Link
        href="/my-reports"
        className="mt-5 inline-block text-blue-800 underline"
      >
        My reports
      </Link>
    </AppShell>
  );
}