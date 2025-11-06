from __future__ import annotations

from datetime import date, timedelta
from typing import List

from sqlalchemy.orm import Session

from ..models import Expense, ExpenseSplit, FrequencyUnit, RecurrenceRule


def add_months(base_date: date, months: int) -> date:
    month = base_date.month - 1 + months
    year = base_date.year + month // 12
    month = month % 12 + 1
    day = min(
        base_date.day,
        [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1],
    )
    return date(year, month, day)


def add_years(base_date: date, years: int) -> date:
    try:
        return base_date.replace(year=base_date.year + years)
    except ValueError:
        return base_date.replace(month=2, day=28, year=base_date.year + years)


def calculate_next_due(rule: RecurrenceRule) -> date:
    if rule.frequency_unit == FrequencyUnit.daily:
        return rule.next_due_date + timedelta(days=rule.interval)
    if rule.frequency_unit == FrequencyUnit.weekly:
        return rule.next_due_date + timedelta(weeks=rule.interval)
    if rule.frequency_unit == FrequencyUnit.monthly:
        return add_months(rule.next_due_date, rule.interval)
    if rule.frequency_unit == FrequencyUnit.yearly:
        return add_years(rule.next_due_date, rule.interval)
    raise ValueError("Frequência desconhecida")


def advance_recurrence(rule: RecurrenceRule) -> None:
    rule.occurrences_generated += 1
    if rule.total_occurrences and rule.occurrences_generated >= rule.total_occurrences:
        rule.is_active = False
    else:
        rule.next_due_date = calculate_next_due(rule)


def fetch_due_recurrences(session: Session, reference: date | None = None) -> List[RecurrenceRule]:
    reference = reference or date.today()
    return (
        session.query(RecurrenceRule)
        .filter(RecurrenceRule.is_active.is_(True))
        .filter(RecurrenceRule.next_due_date <= reference)
        .all()
    )


def instantiate_expense_from_template(session: Session, template_expense: Expense, due_date: date) -> Expense:
    expense = Expense(
        description=template_expense.description,
        amount=template_expense.amount,
        date=due_date,
        category=template_expense.category,
        notes=template_expense.notes,
        paid_by_id=template_expense.paid_by_id,
        account_id=template_expense.account_id,
        recurrence_rule_id=template_expense.recurrence_rule_id,
    )
    for split in template_expense.splits:
        expense.splits.append(
            ExpenseSplit(
                person_id=split.person_id,
                percentage=split.percentage,
                amount=split.amount,
            )
        )
    session.add(expense)
    return expense
