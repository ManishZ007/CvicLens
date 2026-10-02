"use client";

import { FormEvent, useState } from "react";

type Errors = Record<string, string[]>;

export default function RegisterPage() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [age, setAge] = useState("");
  const [password, setPassword] = useState("");

  const [errors, setErrors] = useState<Errors>({});
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setErrors({});
    setSuccess("");
    setLoading(true);

    try {
      const response = await fetch("/api/users/register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          full_name: fullName,
          email,
          age: Number(age),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrors(data.errors || {});
        return;
      }

      setSuccess("Account created successfully!");

      setFullName("");
      setEmail("");
      setAge("");
      setPassword("");
    } catch {
      setErrors({
        __all__: ["Unable to connect to the server."],
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-md">
        <h1 className="mb-6 text-3xl font-bold">Create Account</h1>

        {errors.__all__ && (
          <div className="mb-4 rounded border border-red-300 bg-red-50 p-3 text-red-700">
            {errors.__all__.map((error) => (
              <p key={error}>{error}</p>
            ))}
          </div>
        )}

        {success && (
          <div className="mb-4 rounded border border-green-300 bg-green-50 p-3 text-green-700">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block font-medium">
              Full name
            </label>

            <input
              type="text"
              value={fullName}
              onChange={(event) => setFullName(event.target.value)}
              className="w-full rounded border p-2"
            />

            {errors.full_name && (
              <p className="mt-1 text-sm text-red-600">
                {errors.full_name[0]}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block font-medium">
              Email
            </label>

            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded border p-2"
            />

            {errors.email && (
              <p className="mt-1 text-sm text-red-600">
                {errors.email[0]}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block font-medium">
              Age
            </label>

            <input
              type="number"
              min="13"
              max="120"
              value={age}
              onChange={(event) => setAge(event.target.value)}
              className="w-full rounded border p-2"
            />

            {errors.age && (
              <p className="mt-1 text-sm text-red-600">
                {errors.age[0]}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block font-medium">
              Password
            </label>

            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded border p-2"
            />

            {errors.password && (
              <div className="mt-1 text-sm text-red-600">
                {errors.password.map((error) => (
                  <p key={error}>{error}</p>
                ))}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded bg-black px-4 py-2 text-white disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>
      </div>
    </main>
  );
}