from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils.recurrence import advance_recurrence, fetch_due_recurrences, instantiate_expense_from_template

router = APIRouter(prefix="/recurrences", tags=["recurrences"])


@router.get("/", response_model=list[schemas.RecurrenceRuleRead])
def list_rules(db: Session = Depends(get_db)):
    return db.query(models.RecurrenceRule).order_by(models.RecurrenceRule.next_due_date).all()


@router.post("/", response_model=schemas.RecurrenceRuleRead, status_code=status.HTTP_201_CREATED)
def create_rule(payload: schemas.RecurrenceRuleCreate, db: Session = Depends(get_db)):
    rule = models.RecurrenceRule(**payload.dict())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.put("/{rule_id}", response_model=schemas.RecurrenceRuleRead)
def update_rule(rule_id: int, payload: schemas.RecurrenceRuleUpdate, db: Session = Depends(get_db)):
    rule = db.query(models.RecurrenceRule).filter(models.RecurrenceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regra não encontrada")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(rule, key, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(models.RecurrenceRule).filter(models.RecurrenceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regra não encontrada")
    db.delete(rule)
    db.commit()
    return None


@router.post("/{rule_id}/generate", response_model=list[schemas.ExpenseRead])
def generate_occurrence(rule_id: int, reference_date: date | None = None, db: Session = Depends(get_db)):
    rule = db.query(models.RecurrenceRule).filter(models.RecurrenceRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regra não encontrada")
    if not rule.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Regra inativa")

    template = (
        db.query(models.Expense)
        .filter(models.Expense.recurrence_rule_id == rule.id)
        .order_by(models.Expense.date.asc())
        .first()
    )
    if not template:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não há despesa modelo associada")

    due_date = reference_date or rule.next_due_date
    new_expense = instantiate_expense_from_template(db, template, due_date)
    advance_recurrence(rule)
    db.commit()
    db.refresh(new_expense)

    return (
        db.query(models.Expense)
        .filter(models.Expense.recurrence_rule_id == rule.id)
        .order_by(models.Expense.date.desc())
        .all()
    )


@router.post("/run-due", response_model=dict[str, int])
def generate_due_recurrences(db: Session = Depends(get_db)):
    due_rules = fetch_due_recurrences(db)
    created = 0
    for rule in due_rules:
        template = (
            db.query(models.Expense)
            .filter(models.Expense.recurrence_rule_id == rule.id)
            .order_by(models.Expense.date.asc())
            .first()
        )
        if not template:
            continue
        instantiate_expense_from_template(db, template, rule.next_due_date)
        advance_recurrence(rule)
        created += 1
    db.commit()
    return {"generated": created}
