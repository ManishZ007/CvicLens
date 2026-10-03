import AppShell from "@/components/AppShell";
import { demoComplaints } from "@/lib/demo-complaints";

export default function MyReportsPage() {
  return (
    <AppShell title="My reports">
      <p className="mb-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-900">
        Development preview — sample reports, not your actual complaints.
      </p>

      <div className="space-y-3">
        {demoComplaints.map((report) => (
          <article
            key={report.id}
            className="rounded-xl border border-gray-200 p-4"
          >
            <p className="text-sm text-gray-500">{report.id}</p>

            <h2 className="mt-1 font-semibold">
              {report.description}
            </h2>

            <p className="mt-2 text-sm capitalize">
              Status: {report.status.replaceAll("_", " ")}
            </p>

            <p className="text-sm capitalize">
              Priority: {report.priority}
            </p>
          </article>
        ))}
      </div>
    </AppShell>
  );
}