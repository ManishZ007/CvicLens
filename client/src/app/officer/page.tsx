"use client";

import { useState } from "react";
import { demoComplaints } from "@/lib/demo-complaints";

export default function OfficerPage() {
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");

  const reports = demoComplaints.filter(
    (report) =>
      (!status || report.status === status) &&
      (!category || report.category === category)
  );

  return (
    <main className="min-h-screen bg-[#EDF0F4] p-6 text-[#18202E]">
      <header className="rounded-xl bg-[#1B4F9C] p-5 text-white">
        <h1 className="text-2xl font-bold">CivicLens · Officer console</h1>
        <p>Complaint management</p>
      </header>

      <section className="mt-6 space-y-5 rounded-xl bg-white p-5">
        <p className="rounded-lg bg-amber-50 p-3 text-sm text-amber-900">
          Development preview — sample data only. Officer access comes next.
        </p>

        <div className="flex flex-wrap gap-4">
          <label className="space-y-1">
            <span className="block text-sm">Status</span>
            <select
              value={status}
              onChange={(event) => setStatus(event.target.value)}
              className="rounded-lg border bg-white p-2"
            >
              <option value="">All statuses</option>
              {["submitted", "verified", "assigned", "in_progress", "resolved"]
                .map((value) => (
                  <option key={value} value={value}>
                    {value.replaceAll("_", " ")}
                  </option>
                ))}
            </select>
          </label>

          <label className="space-y-1">
            <span className="block text-sm">Category</span>
            <select
              value={category}
              onChange={(event) => setCategory(event.target.value)}
              className="rounded-lg border bg-white p-2"
            >
              <option value="">All categories</option>
              {["pothole", "garbage", "water", "light", "drain", "other"]
                .map((value) => (
                  <option key={value} value={value}>{value}</option>
                ))}
            </select>
          </label>
        </div>

        <p role="status" className="text-sm">{reports.length} sample reports</p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <caption className="sr-only">Sample civic complaints</caption>
            <thead>
              <tr className="border-b">
                {["ID", "Description", "Category", "Status", "Priority"].map(
                  (heading) => (
                    <th key={heading} scope="col" className="p-3">{heading}</th>
                  )
                )}
              </tr>
            </thead>
            <tbody>
              {reports.map((report) => (
                <tr key={report.id} className="border-b">
                  <td className="whitespace-nowrap p-3">{report.id}</td>
                  <td className="p-3">{report.description}</td>
                  <td className="p-3">{report.category}</td>
                  <td className="p-3">{report.status.replaceAll("_", " ")}</td>
                  <td className="p-3">{report.priority}</td>
                </tr>
              ))}
              {!reports.length && (
                <tr>
                  <td colSpan={5} className="p-6 text-center">
                    No sample complaints match these filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
