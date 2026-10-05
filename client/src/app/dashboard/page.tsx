"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";

export default function DashboardPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        const response = await fetch("/api/users/me/", {
          credentials: "include",
          cache: "no-store",
          signal: controller.signal,
        });

        if (response.status === 401) {
          router.replace("/login");
          return;
        }

        if (!response.ok) {
          throw new Error("Unable to load profile.");
        }

        const user = await response.json();
        setName(user.full_name);
      } catch {
        if (!controller.signal.aborted) {
          setError("Unable to load your dashboard. Please refresh.");
        }
      }
    }

    void load();
    return () => controller.abort();
  }, [router]);

  if (error) {
    return (
      <AppShell title="Dashboard">
        <p role="alert">{error}</p>
      </AppShell>
    );
  }

  if (!name) {
    return (
      <AppShell title="Dashboard">
        <p role="status">Loading...</p>
      </AppShell>
    );
  }

  return (
    <AppShell title={`Namaste, ${name}`}>
      <Link
        href="/report"
        className="block rounded-xl bg-[#F4B400] p-4 text-center font-semibold text-[#2A2000]"
      >
        Report an issue
      </Link>

      <Link
        href="/my-reports"
        className="mt-4 block rounded-xl border border-gray-300 p-4 text-center"
      >
        My reports
      </Link>

      <p className="mt-2 text-sm text-gray-600">
        View your submitted reports and their current status.
      </p>
    </AppShell>
  );
}
