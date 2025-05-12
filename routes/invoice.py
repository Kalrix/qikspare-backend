from fastapi import APIRouter, HTTPException
from models.invoice_model import InvoiceCreate
from database import get_database
from utils.id_generator import generate_id
from bson import ObjectId
from datetime import datetime

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("/create")
async def create_invoice(invoice: InvoiceCreate):
    db = get_database()
    collection = db["invoices"]
    data = invoice.dict()

    # Generate IDs
    invoice_type = data["invoiceType"]
    invoice_id = await generate_id("invoice", f"QIK-{'INV' if invoice_type == 'customer' else 'REV'}")
    order_id = await generate_id("order", "ORDER")

    # Calculate subtotal and tax
    sub_total = 0
    total_tax = 0
    for item in data["items"]:
        base = item["unitPrice"] * item["quantity"]
        discounted = base - item["discountAmount"]
        gst_amount = (discounted * item["gst"]) / 100
        sub_total += discounted
        total_tax += gst_amount

    # Include extra fees
    delivery_charge = data.get("deliveryCharge", 0)
    platform_fee = data.get("platformFee", 0)
    logistics_fee = data.get("logisticsFee", 0)

    total_amount = sub_total + total_tax + delivery_charge + platform_fee + logistics_fee

    # Final document
    data.update({
        "invoiceNumber": invoice_id,
        "orderId": order_id,
        "subTotal": round(sub_total, 2),
        "totalTax": round(total_tax, 2),
        "totalAmount": round(total_amount, 2),
        "status": "paid",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    })

    result = await collection.insert_one(data)

    return {
        "success": True,
        "invoiceId": str(result.inserted_id),
        "invoiceNumber": invoice_id,
        "orderId": order_id
    }


@router.get("/list")
async def list_invoices():
    db = get_database()
    collection = db["invoices"]
    cursor = collection.find()
    invoices = await cursor.to_list(length=1000)
    for inv in invoices:
        inv["_id"] = str(inv["_id"])
    return invoices


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str):
    db = get_database()
    collection = db["invoices"]
    invoice = await collection.find_one({"_id": ObjectId(invoice_id)})
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice["_id"] = str(invoice["_id"])
    return invoice


@router.patch("/update/{invoice_id}")
async def update_invoice(invoice_id: str, data: dict):
    db = get_database()
    collection = db["invoices"]

    # ✅ Prevent _id update
    data.pop("_id", None)

    data["updatedAt"] = datetime.utcnow()
    result = await collection.update_one(
        {"_id": ObjectId(invoice_id)},
        {"$set": data}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Invoice not updated")
    return {"success": True}


@router.delete("/delete/{invoice_id}")
async def delete_invoice(invoice_id: str):
    db = get_database()
    collection = db["invoices"]
    result = await collection.delete_one({"_id": ObjectId(invoice_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"success": True}
