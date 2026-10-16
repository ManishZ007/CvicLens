
"use client";

import { useEffect, useState } from "react";

type Stats = {
  open: number;
  resolved: number;
  overdue: number;
  sla_hours: number;
  average_resolution_hours: number | null;
  by_category: { category: string; count: number }[];
  by_ward: { ward__name: string | null; count: number }[];
};

export default function OfficerStats() {
  const [data, setData] = useState<Stats | null>(null);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setError("");
      setData(null);

      try {
        const response = await fetch(
          "/api/complaints/analytics/",
          {
            credentials: "include",
            cache: "no-store",
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error("Officer analytics unavailable.");
        }

        const result: Stats = await response.json();

        if (!controller.signal.aborted) {
          setData(result);
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
  }, [reload]);

  return (
    <section className="space-y-4 rounded-xl border p-4">
      <h2 className="font-semibold">
        All complaints — summary
      </h2>

      <button
        type="button"
        onClick={() => setReload((value) => value + 1)}
        className="rounded border p-2"
      >
        Refresh summary
      </button>

      {error && (
        <p role="alert" className="text-red-700">
          {error}
        </p>
      )}

      {!data && !error && (
        <p role="status">Loading summary…</p>
      )}

      {data && (
        <>
          <dl className="grid grid-cols-2 gap-3 md:grid-cols-4">
            {[
              ["Open", data.open],
              ["Resolved", data.resolved],
              ["Overdue", data.overdue],
              [
                "Average fix hours",
                data.average_resolution_hours ?? "—",
              ],
            ].map(([label, value]) => (
              <div
                key={String(label)}
                className="rounded-xl bg-blue-50 p-3"
              >
                <dt>{label}</dt>
                <dd className="text-2xl font-bold">
                  {value}
                </dd>
              </div>
            ))}
          </dl>

          <p className="text-sm">
            Demo overdue threshold: {data.sla_hours} hours
            from submission. Totals cover all wards and
            departments.
          </p>

          <table className="w-full text-left">
            <caption>Open by category</caption>
            <thead>
              <tr>
                <th scope="col">Category</th>
                <th scope="col">Count</th>
              </tr>
            </thead>
            <tbody>
              {data.by_category.map((row) => (
                <tr key={row.category}>
                  <td>{row.category}</td>
                  <td>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <table className="w-full text-left">
            <caption>Open by ward</caption>
            <thead>
              <tr>
                <th scope="col">Ward</th>
                <th scope="col">Count</th>
              </tr>
            </thead>
            <tbody>
              {data.by_ward.map((row) => (
                <tr key={row.ward__name ?? "pending"}>
                  <td>
                    {row.ward__name ?? "Routing pending"}
                  </td>
                  <td>{row.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}
