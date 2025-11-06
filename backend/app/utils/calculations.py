from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, List

from sqlalchemy.orm import Session

from ..models import Expense, ExpenseSplit
from ..schemas import DashboardSummary, SettlementSummary


def round_currency(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def apply_split(amount: Decimal, splits: Iterable[ExpenseSplit]) -> None:
    splits = list(splits)
    decimal_splits = [Decimal(str(split.percentage)) for split in splits]
    total_percentage = sum(decimal_splits)
    if total_percentage == 0:
        raise ValueError("Soma das porcentagens é zero")

    running_total = Decimal("0.00")
    for index, split in enumerate(splits):
        if index == len(splits) - 1:
            split.amount = round_currency(amount - running_total)
        else:
            share = round_currency(amount * decimal_splits[index])
            split.amount = share
            running_total += share


def calculate_dashboard(session: Session) -> DashboardSummary:
    expenses = session.query(Expense).all()

    total_paid_by: defaultdict[int, Decimal] = defaultdict(lambda: Decimal("0.00"))
    total_owed_by: defaultdict[int, Decimal] = defaultdict(lambda: Decimal("0.00"))

    total_expenses = Decimal("0.00")

    for expense in expenses:
        amount = Decimal(expense.amount)
        total_expenses += amount
        total_paid_by[expense.paid_by_id] += amount
        for split in expense.splits:
            total_owed_by[split.person_id] += Decimal(split.amount)

    settlements = build_settlements(total_paid_by, total_owed_by)

    return DashboardSummary(
        total_expenses=float(round_currency(total_expenses)),
        total_paid_by={pid: float(round_currency(total)) for pid, total in total_paid_by.items()},
        total_owed_by={pid: float(round_currency(total)) for pid, total in total_owed_by.items()},
        settlements=[SettlementSummary(**settlement) for settlement in settlements],
    )


def build_settlements(total_paid_by: dict[int, Decimal], total_owed_by: dict[int, Decimal]) -> List[dict[str, int | float]]:
    balances: dict[int, Decimal] = {}
    person_ids = set(total_paid_by.keys()) | set(total_owed_by.keys())
    for person_id in person_ids:
        paid = total_paid_by.get(person_id, Decimal("0.00"))
        owed = total_owed_by.get(person_id, Decimal("0.00"))
        balances[person_id] = paid - owed

    receivers = []
    payers = []

    for person_id, balance in balances.items():
        if balance > 0:
            receivers.append([person_id, balance])
        elif balance < 0:
            payers.append([person_id, -balance])

    settlements: List[dict[str, int | float]] = []
    receiver_index = 0
    payer_index = 0

    while receiver_index < len(receivers) and payer_index < len(payers):
        receiver_id, receiver_amount = receivers[receiver_index]
        payer_id, payer_amount = payers[payer_index]

        payment = min(receiver_amount, payer_amount)
        payment = round_currency(payment)

        settlements.append(
            {
                "payer_id": payer_id,
                "receiver_id": receiver_id,
                "amount": float(payment),
            }
        )

        receivers[receiver_index][1] = receiver_amount - payment
        payers[payer_index][1] = payer_amount - payment

        if receivers[receiver_index][1] <= Decimal("0.00"):
            receiver_index += 1
        if payers[payer_index][1] <= Decimal("0.00"):
            payer_index += 1

    return settlements
