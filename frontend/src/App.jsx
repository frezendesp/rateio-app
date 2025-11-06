import { useEffect, useMemo, useState } from "react";
import { Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  Legend,
  LinearScale,
  Tooltip
} from "chart.js";

import ExpensesTable from "./components/ExpensesTable";
import LoadingState from "./components/LoadingState";
import RecurrenceList from "./components/RecurrenceList";
import SettlementsList from "./components/SettlementsList";
import SummaryCard from "./components/SummaryCard";
import {
  fetchAccounts,
  fetchDashboardSummary,
  fetchExpenses,
  fetchPeople,
  fetchRecurrences
} from "./services/api";

ChartJS.register(ArcElement, BarElement, CategoryScale, Legend, LinearScale, Tooltip);

export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [summary, setSummary] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [recurrences, setRecurrences] = useState([]);
  const [people, setPeople] = useState([]);
  const [accounts, setAccounts] = useState([]);

  useEffect(() => {
    async function loadData() {
      try {
        setIsLoading(true);
        const [summaryData, expensesData, recurrencesData, peopleData, accountsData] = await Promise.all([
          fetchDashboardSummary(),
          fetchExpenses(),
          fetchRecurrences(),
          fetchPeople(),
          fetchAccounts()
        ]);
        setSummary(summaryData);
        setExpenses(expensesData);
        setRecurrences(recurrencesData);
        setPeople(peopleData);
        setAccounts(accountsData);
      } catch (err) {
        console.error(err);
        setError("Não foi possível carregar os dados do servidor.");
      } finally {
        setIsLoading(false);
      }
    }

    loadData();
  }, []);

  const peopleById = useMemo(() => Object.fromEntries(people.map((person) => [person.id, person.name])), [people]);
  const accountsById = useMemo(
    () => Object.fromEntries(accounts.map((account) => [account.id, account.name])),
    [accounts]
  );

  const formatCurrency = (value) =>
    Number(value ?? 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });

  const getTotalPaidBy = (matcher) => {
    if (!summary) return "R$ 0,00";
    const entry = Object.entries(peopleById).find(([, name]) => matcher(name ?? ""));
    if (!entry) return "R$ 0,00";
    const [id] = entry;
    const amount = summary.total_paid_by?.[id];
    if (amount === undefined) return "R$ 0,00";
    return formatCurrency(amount);
  };

  const paidBarData = useMemo(() => {
    if (!summary) return null;
    const labels = Object.keys(summary.total_paid_by).map((id) => peopleById[Number(id)] ?? `Pessoa ${id}`);
    const values = Object.values(summary.total_paid_by).map((value) => Number(value));
    return {
      labels,
      datasets: [
        {
          label: "Pago",
          data: values,
          backgroundColor: "rgba(37, 99, 235, 0.8)"
        }
      ]
    };
  }, [summary, peopleById]);

  const owedChartData = useMemo(() => {
    if (!summary) return null;
    const labels = Object.keys(summary.total_owed_by).map((id) => peopleById[Number(id)] ?? `Pessoa ${id}`);
    const values = Object.values(summary.total_owed_by).map((value) => Number(value));
    return {
      labels,
      datasets: [
        {
          label: "Deve",
          data: values,
          backgroundColor: ["#2563eb", "#14b8a6", "#f59e0b", "#ef4444", "#6366f1"]
        }
      ]
    };
  }, [summary, peopleById]);

  if (isLoading) {
    return (
      <main className="mx-auto max-w-6xl space-y-6 p-6">
        <header>
          <h1 className="text-3xl font-bold text-slate-900">Sistema de Rateio Pessoal</h1>
          <p className="mt-2 text-sm text-slate-600">
            Acompanhe em tempo real o rateio das despesas e as recorrências financeiras do casal.
          </p>
        </header>
        <LoadingState />
      </main>
    );
  }

  if (error) {
    return (
      <main className="mx-auto max-w-4xl space-y-4 p-6">
        <header>
          <h1 className="text-3xl font-bold text-slate-900">Sistema de Rateio Pessoal</h1>
        </header>
        <div className="rounded-lg bg-white p-6 text-sm text-red-600 shadow-sm ring-1 ring-red-200">{error}</div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-7xl space-y-8 p-6">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Sistema de Rateio Pessoal</h1>
          <p className="mt-1 text-sm text-slate-600">
            Aplique divisões proporcionais, acompanhe quem pagou e visualize o quanto cada um deve.
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <span className="h-3 w-3 rounded-full bg-emerald-500"></span>
          API conectada
        </div>
      </header>

      {summary ? (
        <section>
          <div className="grid gap-4 sm:grid-cols-3">
            <SummaryCard
              title="Total de Despesas"
              value={formatCurrency(summary.total_expenses)}
              description="Somatório geral das contas registradas"
            />
            <SummaryCard
              title="Pago por Fernando"
              value={getTotalPaidBy((name) => name.toLowerCase() === "fernando")}
              description="Total que saiu da carteira do Fernando"
            />
            <SummaryCard
              title="Pago pela Esposa"
              value={getTotalPaidBy((name) => name.toLowerCase().includes("esposa"))}
              description="Total pago pela esposa"
              accent="secondary"
            />
          </div>
        </section>
      ) : null}

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-lg bg-white p-6 shadow-sm ring-1 ring-slate-200 lg:col-span-2">
          <h2 className="text-lg font-semibold text-slate-800">Pagamentos por pessoa</h2>
          {paidBarData ? (
            <Bar
              data={paidBarData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                  y: {
                    beginAtZero: true
                  }
                }
              }}
              height={240}
            />
          ) : (
            <p className="mt-4 text-sm text-slate-500">Sem dados suficientes para o gráfico.</p>
          )}
        </div>
        <div className="rounded-lg bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="text-lg font-semibold text-slate-800">Participação nas despesas</h2>
          {owedChartData ? <Doughnut data={owedChartData} /> : <p className="mt-4 text-sm text-slate-500">Sem dados.</p>}
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-slate-800">Últimas despesas</h2>
          <ExpensesTable expenses={expenses} peopleById={peopleById} accountsById={accountsById} />
        </div>
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-800">Ajustes de rateio</h2>
          <SettlementsList settlements={summary?.settlements ?? []} peopleById={peopleById} />
        </div>
      </section>

      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-800">Recorrências</h2>
        <RecurrenceList recurrences={recurrences} />
      </section>
    </main>
  );
}
