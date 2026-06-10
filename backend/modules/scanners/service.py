from datetime import datetime
from sqlalchemy.orm import Session
from .models import Scanner
from . import schemas

def get_scanners(db: Session):
    return db.query(Scanner).all()

def get_or_create_scanner(db: Session, identifier: str):
    scanner = db.query(Scanner).filter(Scanner.identifier == identifier).first()
    if not scanner:
        scanner = Scanner(identifier=identifier, name=f"Scanner {identifier}")
        db.add(scanner)
        db.commit()
        db.refresh(scanner)
    return scanner

def update_scanner_last_seen(db: Session, identifier: str):
    if (scanner := db.query(Scanner).filter(Scanner.identifier == identifier).first()):
        scanner.last_seen = datetime.now()
        db.commit()
    return scanner

def update_scanner(db: Session, identifier: str, scanner_in: schemas.ScannerUpdate):
    if not (scanner := db.query(Scanner).filter(Scanner.identifier == identifier).first()):
        return None
    
    if scanner_in.name is not None:
        scanner.name = scanner_in.name
    
    db.commit()
    db.refresh(scanner)
    return scanner
