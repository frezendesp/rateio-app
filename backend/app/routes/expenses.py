from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.calculations import apply_split

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/", response_model=list[schemas.ExpenseRead])
def list_expenses(
    db: Session = Depends(get_db),
    account_id: int | None = Query(None),
    person_id: int | None = Query(None),
):
    query = db.query(models.Expense)
    if account_id is not None:
        query = query.filter(models.Expense.account_id == account_id)
    if person_id is not None:
        query = query.join(models.Expense.splits).filter(models.ExpenseSplit.person_id == person_id)
    return query.order_by(models.Expense.date.desc()).all()


@router.post("/", response_model=schemas.ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(payload: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    amount = Decimal(str(payload.amount))

    expense = models.Expense(
        description=payload.description,
        amount=amount,
        date=payload.date,
        category=payload.category,
        notes=payload.notes,
        paid_by_id=payload.paid_by_id,
        account_id=payload.account_id,
        recurrence_rule_id=payload.recurrence_rule_id,
    )

    for split_payload in payload.splits:
        expense.splits.append(
            models.ExpenseSplit(
                person_id=split_payload.person_id,
                percentage=split_payload.percentage,
                amount=0,
            )
        )

    if not expense.splits:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ao menos um rateio é obrigatório")

    apply_split(amount, expense.splits)

    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/{expense_id}", response_model=schemas.ExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despesa não encontrada")
    return expense


@router.put("/{expense_id}", response_model=schemas.ExpenseRead)
def update_expense(expense_id: int, payload: schemas.ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despesa não encontrada")

    update_data = payload.dict(exclude_unset=True)

    if "splits" in update_data:
        expense.splits.clear()
        for split_payload in update_data.pop("splits") or []:
            expense.splits.append(
                models.ExpenseSplit(
                    person_id=split_payload.person_id,
                    percentage=split_payload.percentage,
                    amount=0,
                )
            )

    if not expense.splits:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ao menos um rateio é obrigatório")

    for key, value in update_data.items():
        if key == "amount" and value is not None:
            setattr(expense, key, Decimal(str(value)))
        else:
            setattr(expense, key, value)

    apply_split(Decimal(str(expense.amount)), expense.splits)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(models.Expense).filter(models.Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Despesa não encontrada")
    db.delete(expense)
    db.commit()
    return None
