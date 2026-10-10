
"use client";

import { useState } from "react";

export type AnalysisPreview = {
  text: string;
  language: string;
  token: string;
  analysis: {
    category: string;
    priority: string;
    translated_text: string | null;
    priority_reason: string;
  };
};

export default function AIAnalysis({
  text,
  language,
  onResult,
  onCategory,
}: {
  text: string;
  language: string;
  onResult: (result: AnalysisPreview) => void;
  onCategory: (category: string) => void;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalysisPreview | null>(null);

  const current =
    result?.text === text.trim() && result.language === language;

  async function analyze() {
    const snapshot = text.trim();

    if (!snapshot) {
      setError("Enter a complaint description before analyzing.");
      return;
    }

    setBusy(true);
    setError("");

    try {
      const csrf = await fetch("/api/complaints/csrf/", {
        credentials: "include",
        cache: "no-store",
      });

      if (!csrf.ok) {
        throw new Error("Could not prepare analysis.");
      }

      const { csrfToken } = await csrf.json();

      const response = await fetch("/api/ai/classify/", {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({
          text: snapshot,
          language,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.errors?.__all__?.join(" ") || "Analysis unavailable."
        );
      }

      const preview: AnalysisPreview = {
        text: snapshot,
        language,
        token: data.analysis_token,
        analysis: data.analysis,
      };

      setResult(preview);
      onResult(preview);
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Analysis failed."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-3 rounded-xl border p-4">
      <button
        type="button"
        disabled={busy || !text.trim()}
        onClick={analyze}
        className="rounded-lg bg-[#1B4F9C] p-3 text-white disabled:opacity-50"
      >
        {busy ? "Analyzing…" : "Analyze complaint"}
      </button>

      <p className="text-sm text-gray-600">
        Hindi/Marathi analysis sends the description to the translation
        service. You can submit without AI.
      </p>

      {error && <p role="alert" className="text-red-700">{error}</p>}

      {result && !current && (
        <p>Description changed. Analyze again.</p>
      )}

      {result && current && (
        <>
          <p>Suggested category: {result.analysis.category}</p>

          <p>Suggested priority: {result.analysis.priority}</p>

          <p className="text-sm">
            {result.analysis.priority_reason}
          </p>

          {result.analysis.translated_text && (
            <p>
              English translation: {result.analysis.translated_text}
            </p>
          )}

          <button
            type="button"
            onClick={() => onCategory(result.analysis.category)}
            className="rounded-lg border p-2"
          >
            Use suggested category
          </button>
        </>
      )}
    </section>
  );
}
