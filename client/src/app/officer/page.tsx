import ReportsList from "@/components/ReportsList";

export default function OfficerPage() {
  return (
    <main className="min-h-screen bg-[#EDF0F4] p-6 text-[#18202E]">
      <header className="rounded-xl bg-[#1B4F9C] p-5 text-white">
        <h1 className="text-2xl font-bold">CivicLens · Officer console</h1>
        <p>Complaint management</p>
      </header>
      <section className="mt-6 rounded-xl bg-white p-5">
        <h2 className="mb-5 text-xl font-semibold">Reported issues</h2>
        <ReportsList officer />
      </section>
    </main>
  );
}
