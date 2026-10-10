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

type Result = {
  results: Report[];
  page: number;
  pages: number;
  count: number;
};

export default function ReportsList({
  officer = false,
  department = "",
  ward = "",
}: {
  officer?: boolean;
  department?: string;
  ward?: string;
}) {
  const router = useRouter();

  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");
  const [search, setSearch] = useState("");
  const [queryText, setQueryText] = useState("");
  const [page, setPage] = useState(1);
  const [retry, setRetry] = useState(0);
  const [result, setResult] = useState<Result | null>(null);
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
          q: queryText,
          department,
          ward,
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

        const data: Result = await response.json();

        if (!controller.signal.aborted) {
          setResult(data);
        }
      } catch (reason) {
        if (!controller.signal.aborted) {
          setError(
            reason instanceof Error
              ? reason.message
              : "Request failed."
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
  }, [
    page,
    status,
    category,
    officer,
    retry,
    router,
    queryText,
    department,
    ward,
  ]);

  return (
    <div className="space-y-4">
      <form
        onSubmit={(event) => {
          event.preventDefault();
          setQueryText(search.trim());
          setPage(1);
        }}
        className="flex flex-wrap items-end gap-2"
      >
        <label className="min-w-0 flex-1">
          Search reports
          <input
            type="search"
            value={search}
            maxLength={200}
            onChange={(event) => setSearch(event.target.value)}
            className="mt-1 w-full rounded-lg border p-2"
            placeholder="Search descriptions"
          />
        </label>

        <button
          type="submit"
          className="rounded-lg border p-2"
        >
          Search
        </button>
      </form>

      <div className="flex flex-wrap gap-3">
        <label className="flex flex-col gap-1 text-sm">
          Status
          <select
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(1);
            }}
            className="rounded-lg border bg-white p-2"
          >
            <option value="">All statuses</option>
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

        <label className="flex flex-col gap-1 text-sm">
          Category
          <select
            value={category}
            onChange={(event) => {
              setCategory(event.target.value);
              setPage(1);
            }}
            className="rounded-lg border bg-white p-2"
          >
            <option value="">All categories</option>
            {[
              "pothole",
              "garbage",
              "water",
              "light",
              "drain",
              "other",
            ].map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </label>
      </div>

      {loading ? (
        <p role="status">Loading reports…</p>
      ) : error ? (
        <div>
          <p role="alert">{error}</p>
          <button
            type="button"
            onClick={() => setRetry((value) => value + 1)}
            className="mt-2 rounded-lg border p-2"
          >
            Retry
          </button>
        </div>
      ) : result ? (
        <>
          <p role="status" className="text-sm text-gray-600">
            {result.count} reports
          </p>

          {!result.results.length && (
            <p>No reports match these filters.</p>
          )}

          {result.results.map((report) => (
            <Link
              key={report.id}
              href={
                officer
                  ? `/officer/${report.id}`
                  : `/my-reports/${report.id}`
              }
              className="block rounded-xl border border-gray-200 p-4"
            >
              <p className="text-sm">
                #{report.id} · {report.category}
              </p>

              <h2 className="break-words font-semibold">
                {report.description}
              </h2>

              <p className="text-sm">
                {report.status.replaceAll("_", " ")} ·{" "}
                {report.priority}
              </p>
            </Link>
          ))}

          <div className="flex items-center justify-between gap-2">
            <button
              type="button"
              disabled={result.page <= 1}
              onClick={() => setPage(result.page - 1)}
              className="rounded-lg border p-2 disabled:opacity-40"
            >
              Previous
            </button>

            <span>
              {result.page} / {result.pages}
            </span>

            <button
              type="button"
              disabled={result.page >= result.pages}
              onClick={() => setPage(result.page + 1)}
              className="rounded-lg border p-2 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </>
      ) : null}
    </div>
  );
}