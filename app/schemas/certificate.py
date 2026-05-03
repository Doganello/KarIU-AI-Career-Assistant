from pydantic import BaseModel
from datetime import date
from typing import Optional


class CertificateCreate(BaseModel):
    title:       str
    issuer:      Optional[str]  = None
    issued_date: Optional[date] = None
    url:         Optional[str]  = None


class CertificateRead(CertificateCreate):
    id: int

    class Config:
        from_attributes = True