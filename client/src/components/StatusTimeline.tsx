type Entry = {
  status: string;
  note: string;
  created_at: string;
};

const steps = [
  ["submitted", "Submitted"],
  ["verified", "Verified"],
  ["assigned", "Assigned"],
  ["in_progress", "In progress"],
  ["resolved", "Resolved"],
];

export default function StatusTimeline({
  status,
  history,
}: {
  status: string;
  history: Entry[];
}) {
  const current = steps.findIndex(([value]) => value === status);

  return (
    <section aria-label="Complaint progress">
      <h2 className="mb-4 font-semibold">Status timeline</h2>

      <ol className="space-y-4">
        {steps.map(([value, label], index) => {
          const entry = [...history].reverse().find(
            (item) => item.status === value
          );

          return (
            <li
              key={value}
              aria-current={index === current ? "step" : undefined}
              className="flex gap-3"
            >
              <span
                aria-hidden="true"
                className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${
                  index <= current
                    ? "bg-[#1B4F9C] text-white"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                {index < current ? "✓" : index + 1}
              </span>

              <div>
                <p className="font-medium">
                  {label}
                  {index === current && " · Current"}
                  {index > current && " · Pending"}
                </p>

                {entry && (
                  <>
                    <p className="text-sm">{entry.note}</p>

                    <time
                      dateTime={entry.created_at}
                      className="text-sm text-gray-500"
                    >
                      {new Date(entry.created_at).toLocaleString()}
                    </time>
                  </>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}