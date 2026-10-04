
"use client";

import { useState } from "react";
import AppShell from "@/components/AppShell";
import PhotoPicker from "@/components/report/PhotoPicker";

export default function ReportPage() {
  const [text, setText] = useState("");
  const [category, setCategory] = useState("");

  return (
    <AppShell title="What is wrong?">
      <div className="space-y-5">

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
        className="w-full rounded-xl bg-[#F4B400] p-3 font-semibold text-[#2A2000] opacity-50"
      >
        <PhotoPicker/>
        Continue
      </button>
      <p className="text-sm">Submission will connect in the next steps.</p>
      </div>
    </AppShell>
  );
}
