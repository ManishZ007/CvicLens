"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import {
  useLanguage,
  type Language,
} from "@/components/LanguageProvider";

export default function ProfilePage() {
  const router = useRouter();
  const { language, saveLanguage } = useLanguage();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [loggingOut, setLoggingOut] = useState(false);

  async function logout() {
    setLoggingOut(true);
    setMessage("");
    try {
      const csrf = await fetch("/api/complaints/csrf/", { credentials: "include", cache: "no-store" });
      if (!csrf.ok) throw new Error("Could not prepare logout.");
      const { csrfToken } = await csrf.json();
      const response = await fetch("/api/users/logout/", {
        method: "POST", credentials: "include", headers: { "X-CSRFToken": csrfToken },
      });
      if (!response.ok) throw new Error("Logout failed. Try again.");
      router.replace("/login");
      router.refresh();
    } catch (reason) {
      setMessage(reason instanceof Error ? reason.message : "Logout failed.");
    } finally {
      setLoggingOut(false);
    }
  }

  return (
    <AppShell title="Language / भाषा">
      <label className="block">
        Preferred language

        <select
          value={language}
          disabled={busy || loggingOut}
          onChange={async (event) => {
            const value = event.target.value as Language;

            setBusy(true);
            setMessage("");

            try {
              await saveLanguage(value);
              setMessage("Saved / सहेजा गया / जतन केले");
            } catch (reason) {
              setMessage(
                reason instanceof Error
                  ? reason.message
                  : "Save failed."
              );
            } finally {
              setBusy(false);
            }
          }}
          className="mt-2 w-full rounded-lg border bg-white p-3"
        >
          <option value="en">English</option>
          <option value="hi">हिन्दी</option>
          <option value="mr">मराठी</option>
        </select>
      </label>

      <p role="status" className="mt-3">
        {busy ? "Saving…" : message}
      </p>
      <button type="button" onClick={logout} disabled={busy || loggingOut}
        className="mt-4 rounded-lg border p-3">
        {loggingOut ? "Logging out…" : "Log out"}
      </button>
    </AppShell>
  );
}
