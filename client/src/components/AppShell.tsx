import Link from "next/link";
import type { ReactNode } from "react";

export default function AppShell({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <main className="min-h-screen bg-[#EDF0F4] p-4 text-[#18202E]">
      <div className="mx-auto max-w-md overflow-hidden rounded-3xl bg-white shadow-lg">
        <header className="bg-[#1B4F9C] p-5 text-white">
          <Link href="/dashboard" className="text-2xl font-bold">
            CivicLens
          </Link>
          <p className="mt-1 text-sm">Report it. Track it. Get it fixed.</p>
        </header>

        <section className="p-5">
          <h1 className="mb-5 text-xl font-bold">{title}</h1>
          {children}
        </section>

        <nav
          aria-label="Citizen navigation"
          className="flex justify-around border-t border-gray-200 p-4 text-sm"
        >
          <Link href="/dashboard">Home</Link>
          <Link href="/report">Report</Link>
        </nav>
      </div>
    </main>
  );
}
