"use client";


import Link from "next/link";
import { useState, type ChangeEvent, type FormEvent } from "react";


type LoginForm = {
  email: string;
  password: string;
};

type FieldErrors = Partial<Record<keyof LoginForm | "__all__", string[]>>;

const initialForm: LoginForm = { email: "", password: "" };

export default function LoginPage() {
  const [form, setForm] = useState<LoginForm>(initialForm);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [loggedInName, setLoggedInName] = useState<string | null>(null);

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: undefined, __all__: undefined }));
  }

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setSubmitting(true);
    setErrors({});

    try {
      const res = await fetch("/api/users/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();

      if (!res.ok) {
        setErrors(data.errors ?? { __all__: ["Login failed. Please try again."] });
        return;
      }

      setLoggedInName(data.full_name);
      setForm(initialForm);
    } catch {
      setErrors({ __all__: ["Could not reach the server. Is the Django backend running?"] });
    } finally {
      setSubmitting(false);
    }
  }

  if (loggedInName) {
    return (
      <main className="flex flex-1 items-center justify-center bg-gray-50 px-4 py-16 dark:bg-gray-950">
        <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-gray-900">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-2xl text-green-600 dark:bg-green-900/40">
            ✓
          </div>
          <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-gray-100">
            Welcome back, {loggedInName}!
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">You are now logged in.</p>
          <Link
            href="/"
            className="mt-6 inline-block rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
          >
            Go to home
          </Link>
        </div>
      </main>
    );
  }

  const inputClass = (hasError: boolean) =>
    `mt-1 w-full rounded-lg border bg-white px-3 py-2 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-950 dark:text-gray-100 ${
      hasError ? "border-red-500" : "border-gray-300 dark:border-gray-700"
    }`;

  return (
    <main className="flex flex-1 items-center justify-center bg-gray-50 px-4 py-16 dark:bg-gray-950">
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 dark:border-gray-800 dark:bg-gray-900">
        <Link href="/" className="text-xl font-bold text-gray-900 dark:text-gray-100">
          Civic<span className="text-blue-600">Lens</span>
        </Link>
        <h1 className="mt-6 text-2xl font-bold text-gray-900 dark:text-gray-100">Log in</h1>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Welcome back! Log in to report and track issues.
        </p>

        {errors.__all__ && (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-400">
            {errors.__all__.join(" ")}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              placeholder="asha@example.com"
              value={form.email}
              onChange={handleChange}
              required
              aria-invalid={!!errors.email}
              className={inputClass(!!errors.email)}
            />
            {errors.email?.map((msg) => (
              <p key={msg} className="mt-1 text-sm text-red-600 dark:text-red-400">
                {msg}
              </p>
            ))}
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              placeholder="Your password"
              value={form.password}
              onChange={handleChange}
              required
              aria-invalid={!!errors.password}
              className={inputClass(!!errors.password)}
            />
            {errors.password?.map((msg) => (
              <p key={msg} className="mt-1 text-sm text-red-600 dark:text-red-400">
                {msg}
              </p>
            ))}

          </div>

          <button
            type="submit"

            disabled={submitting}
            className="w-full rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Logging in..." : "Log in"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Don&apos;t have an account?{" "}
          <Link href="/register" className="font-medium text-blue-600 hover:underline">
            Create one
          </Link>
        </p>

      </div>
    </main>
  );
}