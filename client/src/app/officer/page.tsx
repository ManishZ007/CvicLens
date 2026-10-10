"use client";

import { useEffect, useState } from "react";
import ReportsList from "@/components/ReportsList";

type Option = {
  id: number;
  name: string;
};

export default function OfficerPage() {
  const [department, setDepartment] = useState("");
  const [ward, setWard] = useState("");
  const [departments, setDepartments] = useState<Option[]>([]);
  const [wards, setWards] = useState<Option[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        const response = await fetch(
          "/api/complaints/routing-options/",
          {
            credentials: "include",
            cache: "no-store",
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error("Routing filters unavailable.");
        }

        const data = await response.json();

        if (!controller.signal.aborted) {
          setDepartments(data.departments);
          setWards(data.wards);
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
  }, []);

  return (
    <main className="min-h-screen bg-[#EDF0F4] p-6 text-[#18202E]">
      <header className="rounded-xl bg-[#1B4F9C] p-5 text-white">
        <h1 className="text-2xl font-bold">
          CivicLens · Officer console
        </h1>
      </header>

      <section className="mt-6 space-y-5 rounded-xl bg-white p-5">
        {error && <p role="alert">{error}</p>}

        <div className="flex flex-wrap gap-4">
          <label>
            Department

            <select
              value={department}
              onChange={(event) =>
                setDepartment(event.target.value)
              }
              className="ml-2 rounded-lg border bg-white p-2"
            >
              <option value="">All departments</option>

              {departments.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Ward

            <select
              value={ward}
              onChange={(event) =>
                setWard(event.target.value)
              }
              className="ml-2 rounded-lg border bg-white p-2"
            >
              <option value="">All wards</option>

              {wards.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.name}
                </option>
              ))}
            </select>
          </label>
        </div>

        <ReportsList
          key={`${department}-${ward}`}
          officer
          department={department}
          ward={ward}
        />
      </section>
    </main>
  );
}