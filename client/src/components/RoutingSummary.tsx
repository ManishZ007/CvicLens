
export type RoutingInfo = {
  department: string | null;
  ward: string | null;
  assigned_worker: string | null;
  routing_mode: string;
};

export default function RoutingSummary({
  report,
}: {
  report: RoutingInfo;
}) {
  return (
    <section className="space-y-2 rounded-xl border border-gray-200 p-4">
      <h2 className="font-semibold">Responsible team</h2>

      <p>Department: {report.department || "Pending routing"}</p>
      <p>Ward: {report.ward || "Manual routing required"}</p>
      <p>Worker: {report.assigned_worker || "Not assigned yet"}</p>

      {report.routing_mode === "demo" && (
        <p className="text-sm text-amber-800">
          Demo zone only — not an official municipal ward.
        </p>
      )}

      {report.routing_mode === "outside_demo" && (
        <p className="text-sm text-gray-600">
          This location is outside the configured demo zones.
        </p>
      )}
    </section>
  );
}
