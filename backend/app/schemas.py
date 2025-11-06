from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from .models import FrequencyUnit


class PersonBase(BaseModel):
    name: str
    email: Optional[str] = None
    default_share: float = Field(0.5, ge=0.0, le=1.0)
    is_active: bool = True


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    default_share: Optional[float] = Field(None, ge=0.0, le=1.0)
    is_active: Optional[bool] = None


class PersonRead(PersonBase):
    id: int

    class Config:
        orm_mode = True


class AccountBase(BaseModel):
    name: str
    description: Optional[str] = None
    default_split_fernando: float = Field(0.5, ge=0.0, le=1.0)
    default_split_spouse: float = Field(0.5, ge=0.0, le=1.0)

    @validator("default_split_spouse")
    def validate_total(cls, v, values):
        fernando = values.get("default_split_fernando", 0.0)
        total = fernando + v
        if not 0.99 <= total <= 1.01:
            raise ValueError("A soma dos percentuais padrão deve ser 100% (1.0)")
        return v


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_split_fernando: Optional[float] = Field(None, ge=0.0, le=1.0)
    default_split_spouse: Optional[float] = Field(None, ge=0.0, le=1.0)


class AccountRead(AccountBase):
    id: int

    class Config:
        orm_mode = True


class ExpenseSplitBase(BaseModel):
    person_id: int
    percentage: float = Field(..., ge=0.0, le=1.0)
    amount: Optional[float] = Field(None, ge=0.0)


class ExpenseSplitCreate(ExpenseSplitBase):
    pass


class ExpenseSplitRead(ExpenseSplitBase):
    id: int
    amount: float

    class Config:
        orm_mode = True


class ExpenseBase(BaseModel):
    description: str
    amount: float = Field(..., gt=0)
    date: date
    category: Optional[str] = None
    notes: Optional[str] = None
    paid_by_id: int
    account_id: int
    recurrence_rule_id: Optional[int] = None
    splits: List[ExpenseSplitCreate]

    @validator("splits")
    def validate_splits(cls, splits):
        total = sum(item.percentage for item in splits)
        if not 0.99 <= total <= 1.01:
            raise ValueError("A soma das porcentagens deve ser 100% (1.0)")
        return splits


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    date: Optional[date] = None
    category: Optional[str] = None
    notes: Optional[str] = None
    paid_by_id: Optional[int] = None
    account_id: Optional[int] = None
    recurrence_rule_id: Optional[int] = None
    splits: Optional[List[ExpenseSplitCreate]] = None

    @validator("splits")
    def validate_splits(cls, splits):
        if splits is None:
            return splits
        total = sum(item.percentage for item in splits)
        if not 0.99 <= total <= 1.01:
            raise ValueError("A soma das porcentagens deve ser 100% (1.0)")
        return splits


class ExpenseRead(BaseModel):
    id: int
    description: str
    amount: float
    date: date
    category: Optional[str]
    notes: Optional[str]
    paid_by_id: int
    account_id: int
    recurrence_rule_id: Optional[int]
    created_at: datetime
    splits: List[ExpenseSplitRead]

    class Config:
        orm_mode = True


class RecurrenceRuleBase(BaseModel):
    frequency_unit: FrequencyUnit = FrequencyUnit.monthly
    interval: int = Field(1, ge=1)
    anchor_date: date
    next_due_date: date
    total_occurrences: Optional[int] = Field(None, ge=1)
    is_active: bool = True


class RecurrenceRuleCreate(RecurrenceRuleBase):
    pass


class RecurrenceRuleUpdate(BaseModel):
    frequency_unit: Optional[FrequencyUnit] = None
    interval: Optional[int] = Field(None, ge=1)
    anchor_date: Optional[date] = None
    next_due_date: Optional[date] = None
    total_occurrences: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class RecurrenceRuleRead(RecurrenceRuleBase):
    id: int
    occurrences_generated: int

    class Config:
        orm_mode = True


class SettlementSummary(BaseModel):
    payer_id: int
    receiver_id: int
    amount: float


class DashboardSummary(BaseModel):
    total_expenses: float
    total_paid_by: dict[int, float]
    total_owed_by: dict[int, float]
    settlements: List[SettlementSummary]
