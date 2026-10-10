"use client";

import { useState } from "react";
import AppShell from "@/components/AppShell";
import {
  useLanguage,
  type Language,
} from "@/components/LanguageProvider";

export default function ProfilePage() {
  const { language, saveLanguage } = useLanguage();
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  return (
    <AppShell title="Language / भाषा">
      <label className="block">
        Preferred language

        <select
          value={language}
          disabled={busy}
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
    </AppShell>
  );
}