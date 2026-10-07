"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import PhotoPicker from "@/components/report/PhotoPicker";

export default function ReportPage() {
  const router = useRouter();
  const [text, setText] = useState("");
  const [category, setCategory] = useState("");
  const [photo, setPhoto] = useState<File | null>(null);
  const [latitude, setLatitude] = useState("");
  const [longitude, setLongitude] = useState("");
  const [busy, setBusy] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState("");
  const [reviewing, setReviewing] = useState(false);

  function locate() {
    setError("");

    if (!navigator.geolocation) {
      setError("Location unavailable. Enter coordinates manually.");
      return;
    }

    setLocating(true);

    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setLatitude(String(coords.latitude));
        setLongitude(String(coords.longitude));
        setLocating(false);
      },
      () => {
        setError("Could not get location. Enter coordinates manually.");
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (busy) return;

    if (!text.trim()) {
      setError("Describe the issue.");
      return;
    }

    if (!reviewing) {
      setError("");
      setReviewing(true);
      return;
    }

    setBusy(true);
    setError("");

    try {
      const tokenResponse = await fetch("/api/complaints/csrf/", {
        credentials: "include",
        cache: "no-store",
      });

      if (!tokenResponse.ok) {
        throw new Error("Could not prepare submission.");
      }

      const { csrfToken } = await tokenResponse.json();

      const body = new FormData();
      body.set("description", text.trim());
      body.set("category", category || "other");
      body.set("latitude", latitude);
      body.set("longitude", longitude);

      if (photo) {
        body.set("photo", photo);
      }

      const response = await fetch("/api/complaints/", {
        method: "POST",
        credentials: "include",
        headers: { "X-CSRFToken": csrfToken },
        body,
      });

      if (response.status === 401) {
        setError("Please log in before submitting. Your form is still here.");
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        const errors = data.errors as Record<string, string[]> | undefined;

        throw new Error(
          errors
            ? Object.values(errors).flat().join(" ")
            : "Submission failed."
        );
      }

      router.push(`/my-reports/${data.id}`);
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Submission failed."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <AppShell title="Report an issue">
      <form
        id="complaint-form"
        onSubmit={submit}
        hidden={reviewing}
      >
        <fieldset disabled={busy} className="space-y-5">
          <label className="block">
            Describe the issue
            <textarea
              required
              maxLength={5000}
              rows={5}
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="mt-2 w-full rounded-xl border p-3"
            />
          </label>

          <label className="block">
            Category
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="mt-2 w-full rounded-xl border bg-white p-3"
            >
              <option value="">Other / unsure</option>

              {[
                "pothole",
                "garbage",
                "water",
                "light",
                "drain",
                "other",
              ].map((value) => (
                <option key={value}>{value}</option>
              ))}
            </select>
          </label>

          <PhotoPicker onPhotoChange={setPhoto} />

          <button
            type="button"
            onClick={locate}
            disabled={locating}
            className="rounded-lg border p-3"
          >
            {locating ? "Finding location…" : "Use my location"}
          </button>

          <label className="block">
            Latitude
            <input
              type="number"
              min="-90"
              max="90"
              step="any"
              required
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              className="mt-1 w-full rounded-lg border p-2"
            />
          </label>

          <label className="block">
            Longitude
            <input
              type="number"
              min="-180"
              max="180"
              step="any"
              required
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              className="mt-1 w-full rounded-lg border p-2"
            />
          </label>

          {error && (
            <p role="alert" className="text-red-700">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={locating}
            className="w-full rounded-xl bg-[#F4B400] p-3 font-semibold text-[#2A2000]"
          >
            Review report
          </button>
        </fieldset>
      </form>

      {reviewing && (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold">Check your report</h2>

          <p className="whitespace-pre-wrap break-words">{text}</p>

          <p>Category: {category || "other"}</p>

          <p>
            Location: {latitude}, {longitude}
          </p>

          <p className="break-all">
            Photo: {photo ? photo.name : "Not attached"}
          </p>

          {error && (
            <p role="alert" className="text-red-700">
              {error}
            </p>
          )}

          <div className="flex gap-3">
            <button
              type="button"
              disabled={busy}
              onClick={() => {
                setReviewing(false);
                setError("");
              }}
              className="rounded-lg border p-3"
            >
              Edit
            </button>

            <button
              type="submit"
              form="complaint-form"
              disabled={busy}
              className="rounded-lg bg-[#F4B400] p-3 font-semibold text-[#2A2000]"
            >
              {busy ? "Submitting…" : "Confirm and submit"}
            </button>
          </div>

          <p className="text-sm text-gray-600">
            If the connection fails after submission, check My Reports before
            resubmitting.
          </p>
        </section>
      )}
    </AppShell>
  );
}