"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Report = {
  id: number;
  description: string;
  category: string;
  status: string;
  priority: string;
};

export default function ReportsList({
  officer = false,
}: {
  officer?: boolean;
}) {
  const router = useRouter();
  const [reports, setReports] = useState<Report[]>([]);
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError("");

      try {
        const query = new URLSearchParams({
          page: String(page),
          status,
          category,
        });

        if (officer) {
          query.set("scope", "officer");
        }

        const response = await fetch(`/api/complaints/?${query}`, {
          credentials: "include",
          cache: "no-store",
          signal: controller.signal,
        });

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (response.status === 403) {
          throw new Error("Officer access required.");
        }

        if (!response.ok) {
          throw new Error("Unable to load reports.");
        }

        const data = await response.json();

        setReports(data.results);
        setPages(data.pages);
      } catch (reason) {
        if (!controller.signal.aborted) {
          setError(
            reason instanceof Error ? reason.message : "Request failed."
          );
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => controller.abort();
  }, [page, status, category, officer, router]);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3">
        <label>
          Status
          <select
            value={status}
            onChange={(e) => {
              setStatus(e.target.value);
              setPage(1);
            }}
            className="ml-2 rounded border bg-white p-2"
          >
            <option value="">All</option>

            {[
              "submitted",
              "verified",
              "assigned",
              "in_progress",
              "resolved",
            ].map((value) => (
              <option key={value} value={value}>
                {value.replaceAll("_", " ")}
              </option>
            ))}
          </select>
        </label>

        <label>
          Category
          <select
            value={category}
            onChange={(e) => {
              setCategory(e.target.value);
              setPage(1);
            }}
            className="ml-2 rounded border bg-white p-2"
          >
            <option value="">All</option>

            {["pothole", "garbage", "water", "light", "drain", "other"].map(
              (value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              )
            )}
          </select>
        </label>
      </div>

      {loading ? (
        <p role="status">Loading reports…</p>
      ) : error ? (
        <p role="alert">{error}</p>
      ) : (
        <>
          {!reports.length && <p>No reports found.</p>}

          {reports.map((report) => (
            <Link
              key={report.id}
              href={`/my-reports/${report.id}`}
              className="block rounded-xl border border-gray-200 p-4"
            >
              <p className="text-sm">
                #{report.id} · {report.category}
              </p>

              <h2 className="font-semibold">{report.description}</h2>

              <p className="text-sm">
                {report.status.replaceAll("_", " ")} · {report.priority}
              </p>
            </Link>
          ))}

          <div className="flex items-center justify-between">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="rounded border p-2 disabled:opacity-40"
            >
              Previous
            </button>

            <span>
              {page} / {pages}
            </span>

            <button
              disabled={page >= pages}
              onClick={() => setPage(page + 1)}
              className="rounded border p-2 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}