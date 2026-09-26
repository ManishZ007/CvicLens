"use client";

import Link from "next/link";
import {
  useState,
  type ChangeEvent,
  type FormEvent,
} from "react";

type RegisterForm = {
  full_name: string;
  email: string;
  age: string;
  password: string;
};

type FieldErrors = Partial<
  Record<keyof RegisterForm | "__all__", string[]>
>;

const initialForm: RegisterForm = {
  full_name: "",
  email: "",
  age: "",
  password: "",
};

const fields: {
  name: keyof RegisterForm;
  label: string;
  type: string;
  autoComplete: string;
  placeholder: string;
}[] = [
  {
    name: "full_name",
    label: "Full name",
    type: "text",
    autoComplete: "name",
    placeholder: "Asha Patel",
  },
  {
    name: "email",
    label: "Email",
    type: "email",
    autoComplete: "email",
    placeholder: "asha@example.com",
  },
  {
    name: "age",
    label: "Age",
    type: "number",
    autoComplete: "off",
    placeholder: "21",
  },
  {
    name: "password",
    label: "Password",
    type: "password",
    autoComplete: "new-password",
    placeholder: "At least 8 characters",
  },
];

export default function RegisterPage() {
  const [form, setForm] = useState<RegisterForm>(initialForm);
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [registeredName, setRegisteredName] =
    useState<string | null>(null);

  function handleChange(
    e: ChangeEvent<HTMLInputElement>
  ) {
    const { name, value } = e.target;

    setForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    setErrors((prev) => ({
      ...prev,
      [name]: undefined,
    }));
  }

  async function handleSubmit(
    e: FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    setSubmitting(true);
    setErrors({});

    try {
      const res = await fetch("/api/users/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (!res.ok) {
        setErrors(
          data.errors ?? {
            __all__: [
              "Registration failed. Please try again.",
            ],
          }
        );
        return;
      }

      setRegisteredName(data.full_name);
      setForm(initialForm);
    } catch {
      setErrors({
        __all__: [
          "Could not reach the server. Is the Django backend running?",
        ],
      });
    } finally {
      setSubmitting(false);
    }
  }

  if (registeredName) {
    return (
      <main className="flex flex-1 items-center justify-center bg-gray-50 px-4 py-16 dark:bg-gray-950">
        <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 text-center dark:border-gray-800 dark:bg-gray-900">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-100 text-2xl text-green-600 dark:bg-green-900/40">
            ✓
          </div>

          <h1 className="mt-4 text-2xl font-bold text-gray-900 dark:text-gray-100">
            Welcome, {registeredName}!
          </h1>

          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Your CivicLens account has been created.
          </p>

          <Link
            href="/"
            className="mt-6 inline-block rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
          >
            Back to home
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="flex flex-1 items-center justify-center bg-gray-50 px-4 py-16 dark:bg-gray-950">
      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 dark:border-gray-800 dark:bg-gray-900">
        <Link
          href="/"
          className="text-xl font-bold text-gray-900 dark:text-gray-100"
        >
          Civic<span className="text-blue-600">Lens</span>
        </Link>

        <h1 className="mt-6 text-2xl font-bold text-gray-900 dark:text-gray-100">
          Create your account
        </h1>

        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Join CivicLens to report and track issues in your city.
        </p>

        {errors.__all__ && (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-400">
            {errors.__all__.join(" ")}
          </div>
        )}

        <form
          onSubmit={handleSubmit}
          className="mt-6 space-y-5"
        >
          {fields.map((field) => {
            const fieldErrors = errors[field.name];

            return (
              <div key={field.name}>
                <label
                  htmlFor={field.name}
                  className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                >
                  {field.label}
                </label>

                <input
                  id={field.name}
                  name={field.name}
                  type={field.type}
                  autoComplete={field.autoComplete}
                  placeholder={field.placeholder}
                  value={form[field.name]}
                  onChange={handleChange}
                  required
                  {...(field.name === "age"
                    ? {
                        min: 13,
                        max: 120,
                      }
                    : {})}
                  aria-invalid={!!fieldErrors}
                  className={`mt-1 w-full rounded-lg border bg-white px-3 py-2 text-gray-900 outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-950 dark:text-gray-100 ${
                    fieldErrors
                      ? "border-red-500"
                      : "border-gray-300 dark:border-gray-700"
                  }`}
                />

                {fieldErrors?.map((msg) => (
                  <p
                    key={msg}
                    className="mt-1 text-sm text-red-600 dark:text-red-400"
                  >
                    {msg}
                  </p>
                ))}
              </div>
            );
          })}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting
              ? "Creating account..."
              : "Create account"}
          </button>
        </form>
      </div>
    </main>
  );
}