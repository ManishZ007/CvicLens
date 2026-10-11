
"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useLanguage } from "@/components/LanguageProvider";
import { messages } from "@/lib/i18n";

export default function AppShell({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  const { language } = useLanguage();
  const t = messages[language];

  return (
    <main className="min-h-screen bg-[#EDF0F4] p-4 text-[#18202E]">
      <div className="mx-auto max-w-md overflow-hidden rounded-3xl bg-white shadow-lg">
        <header className="bg-[#1B4F9C] p-5 text-white">
          <Link href="/dashboard" className="text-2xl font-bold">
            CivicLens
          </Link>

          <p className="mt-1 text-sm">{t.tagline}</p>
        </header>

        <section className="p-5">
          <h1 className="mb-5 text-xl font-bold">{title}</h1>
          {children}
        </section>

        <nav
          aria-label="Citizen navigation"
          className="flex flex-wrap justify-around gap-3 border-t border-gray-200 p-4 text-sm"
        >
          <Link href="/dashboard">{t.home}</Link>
          <Link href="/report">{t.report}</Link>
          <Link href="/profile">{t.profile}</Link>
        </nav>
      </div>
    </main>
  );
}
