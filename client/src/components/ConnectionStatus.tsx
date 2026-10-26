"use client";
import { useEffect, useState } from "react";
export default function ConnectionStatus() {
  const [offline, setOffline] = useState(false);
  useEffect(() => {
    const update = () => setOffline(!navigator.onLine);
    update();
    window.addEventListener("online", update);
    window.addEventListener("offline", update);
    if ("serviceWorker" in navigator) void navigator.serviceWorker.register("/sw.js").catch(() => {});
    return () => { window.removeEventListener("online", update); window.removeEventListener("offline", update); };
  }, []);
  return offline ? <p role="status" className="bg-amber-100 p-3 text-center text-sm text-amber-950">
    You are offline. Save your report draft on this device and reconnect before submitting.
  </p> : null;
}
