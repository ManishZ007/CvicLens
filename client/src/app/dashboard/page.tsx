"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

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
        if (!response.ok) throw new Error("Unable to load profile.");

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

  if (error) return <p role="alert" className="p-6">{error}</p>;
  if (!name) return <p className="p-6">Loading…</p>;

  return (
    <main className="mx-auto max-w-md space-y-5 p-6">
      <h1 className="text-2xl font-bold">Namaste, {name}</h1>
      <p>Report it. Track it. Get it fixed.</p>
      <Link
        href="/report"
        className="block rounded-lg bg-blue-900 p-4 text-center text-white"
      >
        Report an issue
      </Link>
    </main>
  );
}
