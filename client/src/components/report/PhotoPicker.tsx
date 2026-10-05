
"use client";

import { useEffect, useState } from "react";

export default function PhotoPicker({
  onPhotoChange,
}: {
  onPhotoChange?: (file: File | null) => void;
}) {
  const [photo, setPhoto] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (preview) return () => URL.revokeObjectURL(preview);
  }, [preview]);

  return (
    <section className="space-y-3">
      <label htmlFor="photo" className="block font-medium">
        Add a photo — optional
      </label>
      <input
        id="photo"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        aria-describedby="photo-help"
        onChange={(event) => {
          const file = event.target.files?.[0];
          event.target.value = "";
          if (!file) return;

          if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
            setError("Choose a JPG, PNG, or WebP image.");
            return;
          }
          if (file.size === 0 || file.size > 5 * 1024 * 1024) {
            setError("Choose a non-empty image smaller than 5 MB.");
            return;
          }

          setError("");
          setPreview(URL.createObjectURL(file));
          setPhoto(file);
          onPhotoChange?.(file);
        }}
        className="block w-full text-sm"
      />
      <p id="photo-help" className="text-sm text-gray-600">
        JPG, PNG, or WebP. Maximum 5 MB. Uploaded when you submit the report.
      </p>
      {error && <p role="alert" className="text-red-700">{error}</p>}

      {photo && preview && (
        <div className="space-y-2">
          {/* Local object URLs are used for upload previews. */}
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={preview}
            alt="Selected civic issue"
            className="h-48 w-full rounded-xl object-contain"
          />
          <p className="break-all text-sm">{photo.name}</p>
          <button
            type="button"
            onClick={() => {
              setPhoto(null);
              setPreview("");
              setError("");
              onPhotoChange?.(null);
            }}
            className="rounded-lg border px-3 py-2"
          >
            Remove photo
          </button>
        </div>
      )}
    </section>
  );
}
