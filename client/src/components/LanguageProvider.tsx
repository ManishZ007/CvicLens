"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { usePathname } from "next/navigation";

export type Language = "en" | "hi" | "mr";

type LanguageContext = {
  language: Language;
  saveLanguage: (language: Language) => Promise<void>;
};

const Context = createContext<LanguageContext | null>(null);

export function LanguageProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [language, setLanguage] = useState<Language>("en");
  const pathname = usePathname();

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        const response = await fetch("/api/users/me/", {
          credentials: "include",
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) return;

        const data = await response.json();

        if (
          !controller.signal.aborted &&
          ["en", "hi", "mr"].includes(data.preferred_language)
        ) {
          setLanguage(data.preferred_language);
        }
      } catch {
        // Keep the current language when offline.
      }
    }

    void load();

    return () => controller.abort();
  }, [pathname]);

  useEffect(() => {
    document.documentElement.lang = language;
  }, [language]);

  async function saveLanguage(value: Language) {
    const csrf = await fetch("/api/complaints/csrf/", {
      credentials: "include",
      cache: "no-store",
    });

    if (!csrf.ok) {
      throw new Error("Unable to prepare preference update.");
    }

    const { csrfToken } = await csrf.json();

    const response = await fetch("/api/users/preferences/", {
      method: "PATCH",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        preferred_language: value,
      }),
    });

    if (!response.ok) {
      throw new Error("Please log in and try again.");
    }

    setLanguage(value);
  }

  return (
    <Context.Provider value={{ language, saveLanguage }}>
      {children}
    </Context.Provider>
  );
}

export function useLanguage() {
  const context = useContext(Context);

  if (!context) {
    throw new Error("LanguageProvider is missing.");
  }

  return context;
}