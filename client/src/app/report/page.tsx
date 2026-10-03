
"use client";

import { useState } from "react";

export default function ReportPage() {
  const [text, setText] = useState("");
  const [category, setCategory] = useState("");

  return (
    <main className="mx-auto max-w-md space-y-5 p-6">
      <h1 className="text-2xl font-bold">What is wrong?</h1>

      <label className="block">
        Describe the issue
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          maxLength={5000}
          rows={5}
          className="mt-2 w-full rounded-lg border p-3"
          placeholder="Describe the problem in your area"
        />
      </label>

      <label className="block">
        Category — optional
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="mt-2 w-full rounded-lg border p-3"
        >
          <option value="">Let the system suggest</option>
          <option value="pothole">Pothole</option>
          <option value="garbage">Garbage</option>
          <option value="water">Water leak</option>
          <option value="light">Streetlight</option>
          <option value="drain">Drainage</option>
          <option value="other">Other</option>
        </select>
      </label>

      <button
        disabled
        className="w-full rounded-lg bg-blue-900 p-3 text-white opacity-50"
      >
        Continue
      </button>
      <p className="text-sm">Submission will connect in the next steps.</p>
    </main>
  );
}
