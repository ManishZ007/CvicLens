export async function csrfToken(): Promise<string> {
  const response = await fetch("/api/complaints/csrf/", { credentials: "include", cache: "no-store" });
  if (!response.ok) throw new Error("Unable to prepare request. Check the server connection.");
  return (await response.json()).csrfToken;
}
