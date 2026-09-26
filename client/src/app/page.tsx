const steps = [
  {
    number: "01",
    title: "Spot an issue",
    description:
      "See a pothole, overflowing garbage, a broken streetlight or a water leak in your area? Open CivicLens.",
  },
  {
    number: "02",
    title: "Report it",
    description:
      "Take a photo, add a short description and pin the location on the map. It takes less than a minute.",
  },
  {
    number: "03",
    title: "Authorities act",
    description:
      "Your report goes to the right local department. They review it, assign it and start working on it.",
  },
  {
    number: "04",
    title: "Track progress",
    description:
      "Follow your report from Submitted → In Progress → Resolved, and see when your street is fixed.",
  },
];

const features = [
  {
    title: "Photo & location",
    description: "Every report includes a picture and an exact map location, so nothing gets lost.",
  },
  {
    title: "Live status",
    description: "See the current status of every issue you reported, at any time.",
  },
  {
    title: "Community upvotes",
    description: "Support issues others have reported so the most urgent problems get fixed first.",
  },
  {
    title: "Transparency",
    description: "Anyone can see what has been reported and what has been fixed in their city.",
  },
];

const roles = [
  {
    title: "For citizens",
    points: [
      "Report problems in your neighbourhood",
      "Upvote issues that affect you",
      "Get updates until the issue is resolved",
    ],
  },
  {
    title: "For authorities",
    points: [
      "See all reported issues in one dashboard",
      "Assign issues to the right team",
      "Update status and close resolved issues",
    ],
  },
];

export default function Home() {
  return (
    <main className="flex-1 bg-white text-gray-900 dark:bg-gray-950 dark:text-gray-100">
      {/* Navbar */}
      <header className="border-b border-gray-200 dark:border-gray-800">
        <nav className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <span className="text-xl font-bold">
            Civic<span className="text-blue-600">Lens</span>
          </span>
          <div className="flex gap-6 text-sm font-medium">
            <a href="#how-it-works" className="hover:text-blue-600">
              How it works
            </a>
            <a href="#features" className="hover:text-blue-600">
              Features
            </a>
          </div>
        </nav>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-4 py-20 text-center">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
          See a problem in your city? <br className="hidden sm:block" />
          <span className="text-blue-600">Report it. Track it. Get it fixed.</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-600 dark:text-gray-400">
          CivicLens connects citizens with local authorities. Report civic issues like potholes,
          garbage and broken streetlights, and follow them until they are resolved.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-4">
          <a
            href="#how-it-works"
            className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700"
          >
            See how it works
          </a>
          <a
            href="#features"
            className="rounded-lg border border-gray-300 px-6 py-3 font-semibold hover:bg-gray-100 dark:border-gray-700 dark:hover:bg-gray-900"
          >
            Explore features
          </a>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="bg-gray-50 py-20 dark:bg-gray-900">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="text-center text-3xl font-bold">How it works</h2>
          <p className="mt-3 text-center text-gray-600 dark:text-gray-400">
            From spotting a problem to getting it fixed, in four simple steps.
          </p>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {steps.map((step) => (
              <div
                key={step.number}
                className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-950"
              >
                <span className="text-sm font-bold text-blue-600">{step.number}</span>
                <h3 className="mt-2 text-lg font-semibold">{step.title}</h3>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="text-center text-3xl font-bold">Features</h2>
          <div className="mt-12 grid gap-6 sm:grid-cols-2">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="rounded-xl border border-gray-200 p-6 dark:border-gray-800"
              >
                <h3 className="text-lg font-semibold">{feature.title}</h3>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Who is it for */}
      <section className="bg-gray-50 py-20 dark:bg-gray-900">
        <div className="mx-auto max-w-6xl px-4">
          <h2 className="text-center text-3xl font-bold">Who is it for?</h2>
          <div className="mt-12 grid gap-6 md:grid-cols-2">
            {roles.map((role) => (
              <div
                key={role.title}
                className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-950"
              >
                <h3 className="text-xl font-semibold text-blue-600">{role.title}</h3>
                <ul className="mt-4 space-y-2 text-gray-700 dark:text-gray-300">
                  {role.points.map((point) => (
                    <li key={point} className="flex gap-2">
                      <span className="text-blue-600">✓</span>
                      {point}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-8 text-center text-sm text-gray-500 dark:border-gray-800">
        © {new Date().getFullYear()} CivicLens. Building better cities, together.
      </footer>
    </main>
  );
}
