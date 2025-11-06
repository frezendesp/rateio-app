export default function RecurrenceList({ recurrences = [] }) {
  if (recurrences.length === 0) {
    return (
      <div className="rounded-lg bg-white p-6 text-sm text-slate-500 shadow-sm ring-1 ring-slate-200">
        Nenhuma recorrência configurada.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-slate-200">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Frequência</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Próxima Execução</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Ocorrências</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white text-sm">
          {recurrences.map((rule) => (
            <tr key={rule.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 text-slate-600">
                A cada {rule.interval} {translateUnit(rule.frequency_unit)}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {new Date(rule.next_due_date).toLocaleDateString("pt-BR")}
              </td>
              <td className="px-4 py-3 text-slate-600">
                {rule.occurrences_generated}
                {rule.total_occurrences ? ` de ${rule.total_occurrences}` : ""}
              </td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                    rule.is_active ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-600"
                  }`}
                >
                  {rule.is_active ? "Ativa" : "Inativa"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function translateUnit(unit) {
  switch (unit) {
    case "daily":
      return "dia(s)";
    case "weekly":
      return "semana(s)";
    case "monthly":
      return "mês(es)";
    case "yearly":
      return "ano(s)";
    default:
      return unit;
  }
}
