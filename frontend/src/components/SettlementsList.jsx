export default function SettlementsList({ settlements = [], peopleById = {} }) {
  if (settlements.length === 0) {
    return (
      <div className="rounded-lg bg-white p-6 text-sm text-slate-500 shadow-sm ring-1 ring-slate-200">
        Nenhum ajuste necessário no momento.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {settlements.map((settlement, index) => (
        <div
          key={`${settlement.payer_id}-${settlement.receiver_id}-${index}`}
          className="flex items-center justify-between rounded-lg bg-white p-4 shadow-sm ring-1 ring-slate-200"
        >
          <div>
            <p className="text-sm font-medium text-slate-700">
              {peopleById[settlement.payer_id] ?? "Alguém"} deve
              <span className="font-semibold text-primary">
                {" "}
                {Number(settlement.amount).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
              </span>
              {" "}
              para {peopleById[settlement.receiver_id] ?? "alguém"}.
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
