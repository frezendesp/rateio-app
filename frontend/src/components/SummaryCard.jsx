export default function SummaryCard({ title, value, description, accent = "primary" }) {
  const accentClass = accent === "primary" ? "text-primary" : "text-secondary";

  return (
    <div className="rounded-lg bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <h3 className="text-sm font-medium text-slate-500">{title}</h3>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
      {description ? <p className={`mt-3 text-sm ${accentClass}`}>{description}</p> : null}
    </div>
  );
}
