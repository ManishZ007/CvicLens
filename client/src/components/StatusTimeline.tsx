
"use client";

import { useLanguage } from "@/components/LanguageProvider";
import { messages } from "@/lib/i18n";
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
  const { language } = useLanguage();
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
               {messages[language].statuses[value] || label}
                  {index === current && " · Current"}
                  {index > current && " · Pending"}
                </p>

                {entry && index <= current && (
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
<details className="mt-4 rounded-xl border p-3">
  <summary className="cursor-pointer font-medium">Complete activity history</summary>
  <ol className="mt-3 space-y-3">
    {history.map((entry, index) => (
      <li key={`${entry.created_at}-${index}`} className="border-l-2 border-blue-200 pl-3">
        <p>{messages[language].statuses[entry.status] || entry.status.replaceAll("_", " ")}</p>
        <p className="whitespace-pre-wrap">{entry.note}</p>
        <time dateTime={entry.created_at} className="text-sm text-gray-600">
          {new Date(entry.created_at).toLocaleString()}
        </time>
      </li>
    ))}
  </ol>
</details>
    </section>
  );
}
