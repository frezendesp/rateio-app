from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import List

from sqlalchemy import Boolean, Column, Date, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class FrequencyUnit(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(120), unique=True)
    default_share: Mapped[float] = mapped_column(Float, default=0.5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    expenses_paid: Mapped[List["Expense"]] = relationship(back_populates="paid_by", cascade="all, delete-orphan", foreign_keys="Expense.paid_by_id")
    splits: Mapped[List["ExpenseSplit"]] = relationship(back_populates="person", cascade="all, delete-orphan")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    default_split_fernando: Mapped[float] = mapped_column(Float, default=0.5)
    default_split_spouse: Mapped[float] = mapped_column(Float, default=0.5)

    expenses: Mapped[List["Expense"]] = relationship(back_populates="account", cascade="all, delete-orphan")


class RecurrenceRule(Base):
    __tablename__ = "recurrence_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    frequency_unit: Mapped[FrequencyUnit] = mapped_column(SqlEnum(FrequencyUnit), default=FrequencyUnit.monthly)
    interval: Mapped[int] = mapped_column(Integer, default=1)
    anchor_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_occurrences: Mapped[int | None] = mapped_column(Integer)
    occurrences_generated: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    expenses: Mapped[List["Expense"]] = relationship(back_populates="recurrence_rule")


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    category: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    paid_by_id: Mapped[int] = mapped_column(ForeignKey("people.id"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    recurrence_rule_id: Mapped[int | None] = mapped_column(ForeignKey("recurrence_rules.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    paid_by: Mapped[Person] = relationship(back_populates="expenses_paid", foreign_keys=[paid_by_id])
    account: Mapped[Account] = relationship(back_populates="expenses")
    splits: Mapped[List["ExpenseSplit"]] = relationship(back_populates="expense", cascade="all, delete-orphan")
    recurrence_rule: Mapped[RecurrenceRule | None] = relationship(back_populates="expenses")


class ExpenseSplit(Base):
    __tablename__ = "expense_splits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    expense_id: Mapped[int] = mapped_column(ForeignKey("expenses.id", ondelete="CASCADE"), nullable=False)
    person_id: Mapped[int] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"), nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    expense: Mapped[Expense] = relationship(back_populates="splits")
    person: Mapped[Person] = relationship(back_populates="splits")
