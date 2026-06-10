from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from . import schemas
from ...core.database import get_db
from . import service

router = APIRouter(prefix="/api/scanners", tags=["scanners"])

@router.get("/", response_model=List[schemas.ScannerResponse])
def get_scanners(db: Session = Depends(get_db)):
    return service.get_scanners(db)

@router.put("/{identifier}", response_model=schemas.ScannerResponse)
def update_scanner(identifier: str, scanner_in: schemas.ScannerUpdate, db: Session = Depends(get_db)):
    if not (scanner := service.update_scanner(db, identifier, scanner_in)):
        raise HTTPException(status_code=404, detail="Scanner not found")
    return scanner
