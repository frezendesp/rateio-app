export default function ExpensesTable({ expenses = [], peopleById = {}, accountsById = {} }) {
  return (
    <div className="overflow-hidden rounded-lg bg-white shadow-sm ring-1 ring-slate-200">
      <table className="min-w-full divide-y divide-slate-200">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Data</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Descrição</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Conta</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">Pago por</th>
            <th className="px-4 py-3 text-right text-xs font-semibold uppercase tracking-wide text-slate-500">Valor</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 bg-white text-sm">
          {expenses.length === 0 ? (
            <tr>
              <td colSpan={5} className="px-4 py-6 text-center text-slate-500">
                Nenhuma despesa cadastrada ainda.
              </td>
            </tr>
          ) : (
            expenses.map((expense) => (
              <tr key={expense.id} className="hover:bg-slate-50">
                <td className="px-4 py-3 whitespace-nowrap text-slate-600">
                  {new Date(expense.date).toLocaleDateString("pt-BR")}
                </td>
                <td className="px-4 py-3">
                  <p className="font-medium text-slate-900">{expense.description}</p>
                  {expense.category ? <p className="text-xs text-slate-500">{expense.category}</p> : null}
                </td>
                <td className="px-4 py-3 text-slate-600">{accountsById[expense.account_id] ?? "-"}</td>
                <td className="px-4 py-3 text-slate-600">{peopleById[expense.paid_by_id] ?? "-"}</td>
                <td className="px-4 py-3 text-right font-semibold text-slate-900">
                  {Number(expense.amount).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
