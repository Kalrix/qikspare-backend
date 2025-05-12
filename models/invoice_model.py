from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PartyInfo(BaseModel):
    userId: str
    name: str
    address: str
    phone: str
    email: Optional[str] = ""
    gstin: Optional[str] = ""

class InvoiceItem(BaseModel):
    partName: str
    modelNo: str
    category: str
    unitPrice: float
    quantity: int
    discountAmount: float
    discountPercent: float
    gst: float

class InvoiceCreate(BaseModel):
    invoiceType: str  # "customer" or "platform"
    buyer: Optional[PartyInfo] = None
    seller: PartyInfo
    items: List[InvoiceItem]
    deliveryCharge: Optional[float] = 0.0
    paymentMode: str
    platformFee: Optional[float] = 0.0
    invoiceDate: str  # ISO Date
