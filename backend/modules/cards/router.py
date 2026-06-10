from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import schemas
from ...core.database import get_db
from . import service

router = APIRouter(prefix="/api/cards", tags=["cards"])

@router.get("/", response_model=List[schemas.CardResponse])
def get_cards(db: Session = Depends(get_db)):
    return service.get_cards(db)

@router.post("/", response_model=schemas.CardResponse)
def add_card(card_in: schemas.CardCreate, db: Session = Depends(get_db)):
    return service.add_card(db, card_in)

@router.put("/{uid}", response_model=schemas.CardResponse)
def update_card(uid: str, card_in: schemas.CardUpdate, db: Session = Depends(get_db)):
    if not (card := service.update_card(db, uid, card_in)):
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@router.delete("/{uid}")
def delete_card(uid: str, db: Session = Depends(get_db)):
    if not service.delete_card(db, uid):
        raise HTTPException(status_code=404, detail="Card not found")
    return {"message": "Card deleted successfully"}
