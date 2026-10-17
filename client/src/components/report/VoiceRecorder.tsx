"use client";
import { useEffect, useRef, useState } from "react";

export default function VoiceRecorder({ language, onApply }: {
  language: "en" | "hi" | "mr";
  onApply: (text: string) => boolean;
}) {
  const recorder = useRef<MediaRecorder | null>(null);
  const stream = useRef<MediaStream | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive = useRef(true);
  const request = useRef<AbortController | null>(null);
  const [recording, setRecording] = useState(false);
  const [busy, setBusy] = useState(false);
  const [audio, setAudio] = useState<Blob | null>(null);
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
      request.current?.abort();
      if (timer.current) clearTimeout(timer.current);
      if (recorder.current?.state === "recording") recorder.current.stop();
      stream.current?.getTracks().forEach(track => track.stop());
    };
  }, []);
  useEffect(() => () => { if (url) URL.revokeObjectURL(url); }, [url]);

  function stop() {
    if (recorder.current?.state === "recording") recorder.current.stop();
  }

  async function start() {
    setBusy(true);
    setError("");
    try {
      if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        throw new Error("Recording needs HTTPS or localhost and a supported browser.");
      }
      const input = await navigator.mediaDevices.getUserMedia({ audio: true });
      if (!alive.current) { input.getTracks().forEach(t => t.stop()); return; }
      stream.current = input;
      const mimeType = ["audio/webm", "audio/ogg", "audio/mp4"]
        .find(type => MediaRecorder.isTypeSupported(type));
      const next = new MediaRecorder(input, mimeType ? { mimeType } : undefined);
      recorder.current = next;
      const chunks: Blob[] = [];
      next.ondataavailable = event => { if (event.data.size) chunks.push(event.data); };
      next.onstop = () => {
        if (timer.current) clearTimeout(timer.current);
        input.getTracks().forEach(t => t.stop());
        if (!alive.current) return;
        const blob = new Blob(chunks, { type: next.mimeType });
        setAudio(blob);
        setUrl(URL.createObjectURL(blob));
        setRecording(false);
      };
      next.onerror = () => {
        input.getTracks().forEach(t => t.stop());
        if (alive.current) { setRecording(false); setError("Recording failed. Try again."); }
      };
      setText("");
      setAudio(null);
      setUrl("");
      next.start();
      setRecording(true);
      // Leave room for browser stop-event latency within the API's 60-second limit.
      timer.current = setTimeout(stop, 59000);
    } catch (reason) {
      stream.current?.getTracks().forEach(t => t.stop());
      if (alive.current) setError(reason instanceof Error ? reason.message : "Microphone unavailable.");
    } finally { if (alive.current) setBusy(false); }
  }

  async function transcribe() {
    if (!audio || busy) return;
    setBusy(true);
    setError("");
    const controller = new AbortController();
    request.current = controller;
    try {
      const csrf = await fetch("/api/complaints/csrf/", {
        credentials: "include", cache: "no-store", signal: controller.signal,
      });
      if (!csrf.ok) throw new Error("Could not prepare transcription.");
      const { csrfToken } = await csrf.json();
      const body = new FormData();
      body.set("audio", audio, "recording");
      body.set("language", language);
      const response = await fetch("/api/ai/transcribe/", {
        method: "POST", credentials: "include", body,
        headers: { "X-CSRFToken": csrfToken }, signal: controller.signal,
      });
      if (response.status === 401) throw new Error("Please sign in first.");
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || "Transcription failed.");
      if (alive.current) setText(result.text);
    } catch (reason) {
      if (!controller.signal.aborted && alive.current)
        setError(reason instanceof Error ? reason.message : "Transcription failed.");
    } finally { if (alive.current) setBusy(false); }
  }

  return <section className="space-y-3 rounded-xl border p-3">
    <p>Voice report: record up to 59 seconds, then review the text.</p>
    <button type="button" disabled={busy} onClick={recording ? stop : start}
      className="rounded border p-2">{recording ? "Stop recording" : "Record voice"}</button>
    {url && <audio controls src={url} className="w-full" />}
    {audio && <button type="button" disabled={busy || recording}
      onClick={transcribe} className="rounded border p-2">
      {busy ? "Transcribing…" : "Transcribe recording"}
    </button>}
    <label className="block">Editable transcript
      <textarea value={text} onChange={event => setText(event.target.value)}
        disabled={busy || recording} maxLength={5000} rows={3} className="w-full rounded border p-2" />
    </label>
    <button type="button" disabled={!text.trim() || busy || recording}
      onClick={() => { if (onApply(text.trim())) setText(""); }}
      className="rounded border p-2">Append transcript to description</button>
    {error && <p role="alert" className="text-red-700">{error}</p>}
  </section>;
}
