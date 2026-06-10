from sqlalchemy.orm import Session
from .models import Card, AccessLog
from . import schemas
from fastapi import HTTPException

def get_cards(db: Session):
    return db.query(Card).all()

def add_card(db: Session, card_in: schemas.CardCreate):
    if db.query(Card).filter(Card.uid == card_in.uid).first():
        raise HTTPException(status_code=400, detail="UID already registered")
    
    card = Card(**card_in.model_dump())
    db.add(card)
    db.commit()
    db.refresh(card)
    return card

def update_card(db: Session, uid: str, card_in: schemas.CardUpdate):
    if not (card := db.query(Card).filter(Card.uid == uid).first()):
        return None
    
    update_data = card_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(card, key, value)
    
    db.commit()
    db.refresh(card)
    return card

def delete_card(db: Session, uid: str):
    if not (card := db.query(Card).filter(Card.uid == uid).first()):
        return False
    
    db.delete(card)
    db.commit()
    return True

def get_card_by_tracker_mac(db: Session, mac: str):
    return db.query(Card).filter(Card.tracker_mac == mac).first()

def process_card_scan(db: Session, uid: str):
    """Business logic for processing a card scan. Returns (authorized, name, status)"""
    
    authorized = False
    name = "Unknown"
    status = "unknown"

    if (card :=  db.query(Card).filter(Card.uid == uid).first()):
        name = card.name
        if card.is_active:
            authorized = True
            status = "authorized"
        else:
            status = "inactive"
    
    # Log the access
    access_log = AccessLog(uid=uid, status=status)
    db.add(access_log)
    db.commit()
    
    return authorized, name, status
