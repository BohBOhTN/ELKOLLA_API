from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from models import Invoice, Item
from database import SessionLocal, init_db
from pydantic import BaseModel
from utils import number_to_words, generate_invoice_number
from datetime import datetime
from typing import List, Optional
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.sql import func
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Initialize the database
init_db()

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the response models first
class ItemResponse(BaseModel):
    reference: str
    quantity: int
    designation: str
    unit_price: float
    total_price: float

class InvoiceResponse(BaseModel):
    invoice_number: str
    subtotal_ht: float
    montant_tva: float
    timbre_price: float
    final_price: float
    final_price_in_words: str

class InvoiceDetailResponse(BaseModel):
    invoice_number: str
    client_name: str
    vat_number: str
    address: str
    invoice_date: str
    subtotal_ht: float
    montant_tva: float
    timbre_price: float
    final_price: float
    final_price_in_words: str
    items: List[ItemResponse]

# Define request models
class ItemRequest(BaseModel):
    reference: str
    quantity: int
    designation: str
    unit_price: float

class InvoiceRequest(BaseModel):
    client_name: str
    vat_number: str
    address: str
    invoice_date: str
    items: list[ItemRequest]

# Dependency for getting the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/create_invoice", response_model=InvoiceResponse)
def create_invoice(invoice_request: InvoiceRequest, db: Session = Depends(get_db)):
    # Convert invoice_date from string to datetime.date
    invoice_date_obj = datetime.strptime(invoice_request.invoice_date, "%d/%m/%Y").date()

    # 1. Calculate Subtotal HT
    subtotal_ht = sum(item.unit_price * item.quantity for item in invoice_request.items)

    # 2. Calculate Montant TVA (7%)
    montant_tva = subtotal_ht * 0.07

    # 3. Fixed Timbre price (1 dinar, formatted to 3 decimal places)
    timbre_price = 1.000

    # 4. Final price
    final_price = subtotal_ht + montant_tva + timbre_price

    # Round values to 3 decimal places and format with commas
    subtotal_ht = f"{subtotal_ht:,.3f}"
    montant_tva = f"{montant_tva:,.3f}"
    timbre_price = f"{timbre_price:,.3f}"
    final_price = f"{final_price:,.3f}"

    # 5. Generate invoice number (MMYY_XXX)
    invoice_number = generate_invoice_number(invoice_request.invoice_date, db)

    # 6. Convert final price to words
    final_price_in_words = number_to_words(float(final_price.replace(',', '')))

    # 7. Create invoice record in the database
    invoice = Invoice(
        client_name=invoice_request.client_name,
        vat_number=invoice_request.vat_number,
        address=invoice_request.address,
        invoice_date=invoice_date_obj,  # Use the converted date object here
        invoice_number=invoice_number,
        subtotal_ht=float(subtotal_ht.replace(',', '')),
        montant_tva=float(montant_tva.replace(',', '')),
        timbre_price=float(timbre_price.replace(',', '')),
        final_price=float(final_price.replace(',', '')),
        final_price_in_words=final_price_in_words
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Create item records and link them to the invoice
    for item in invoice_request.items:
        db_item = Item(
            invoice_id=invoice.invoice_id,
            reference=item.reference,
            quantity=item.quantity,
            designation=item.designation,
            unit_price=item.unit_price,
            total_price=float(f"{item.unit_price * item.quantity:,.3f}".replace(',', ''))  # Format total_price
        )
        db.add(db_item)
    
    db.commit()

    return InvoiceResponse(
        invoice_number=invoice_number,
        subtotal_ht=float(subtotal_ht.replace(',', '')),
        montant_tva=float(montant_tva.replace(',', '')),
        timbre_price=float(timbre_price.replace(',', '')),
        final_price=float(final_price.replace(',', '')),
        final_price_in_words=final_price_in_words
    )


@app.get("/invoices", response_model=List[InvoiceResponse])
def get_invoices(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Invoice)

    if year:
        query = query.filter(func.extract('year', Invoice.invoice_date) == year)
    if month:
        query = query.filter(func.extract('month', Invoice.invoice_date) == month)
    if day:
        query = query.filter(func.extract('day', Invoice.invoice_date) == day)

    invoices = query.all()

    # Convert to response model
    invoice_responses = [
        InvoiceResponse(
            invoice_number=invoice.invoice_number,
            subtotal_ht=float(f"{invoice.subtotal_ht:.3f}"),
            montant_tva=float(f"{invoice.montant_tva:.3f}"),
            timbre_price=float(f"{invoice.timbre_price:.3f}"),
            final_price=float(f"{invoice.final_price:.3f}"),
            final_price_in_words=invoice.final_price_in_words,
        )
        for invoice in invoices
    ]

    return JSONResponse(content=jsonable_encoder(invoice_responses))

@app.delete("/delete_invoice")
def delete_invoice(
    invoice_id: Optional[int] = None, 
    invoice_number: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    """
    Delete an invoice by ID or invoice number.
    - invoice_id: int -> Delete based on invoice ID.
    - invoice_number: str -> Delete based on invoice number.
    """
    if not invoice_id and not invoice_number:
        raise HTTPException(status_code=400, detail="You must provide either invoice_id or invoice_number.")
    
    # Find the invoice
    invoice_query = db.query(Invoice)
    
    if invoice_id:
        invoice_query = invoice_query.filter(Invoice.invoice_id == invoice_id)
    elif invoice_number:
        invoice_query = invoice_query.filter(Invoice.invoice_number == invoice_number)
    
    invoice = invoice_query.first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    
    # Delete associated items first
    db.query(Item).filter(Item.invoice_id == invoice.invoice_id).delete()

    # Delete the invoice
    db.delete(invoice)
    db.commit()
    
    return {"message": f"Invoice has been deleted successfully."}

@app.get("/invoice_details", response_model=InvoiceDetailResponse)
def invoice_details(
    invoice_number: Optional[str] = None,
    invoice_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if not invoice_number and not invoice_id:
        raise HTTPException(status_code=400, detail="You must provide either invoice_id or invoice_number.")
    
    invoice_query = db.query(Invoice).join(Item, Invoice.invoice_id == Item.invoice_id)
    
    if invoice_id:
        invoice_query = invoice_query.filter(Invoice.invoice_id == invoice_id)
    elif invoice_number:
        invoice_query = invoice_query.filter(Invoice.invoice_number == invoice_number)
    
    invoice = invoice_query.first()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    
    items = db.query(Item).filter(Item.invoice_id == invoice.invoice_id).all()

    invoice_detail_response = InvoiceDetailResponse(
        invoice_number=invoice.invoice_number,
        client_name=invoice.client_name,
        vat_number=invoice.vat_number,
        address=invoice.address,
        invoice_date=invoice.invoice_date.strftime("%d/%m/%Y"),
        subtotal_ht=float(f"{invoice.subtotal_ht:.3f}"),
        montant_tva=float(f"{invoice.montant_tva:.3f}"),
        timbre_price=float(f"{invoice.timbre_price:.3f}"),
        final_price=float(f"{invoice.final_price:.3f}"),
        final_price_in_words=invoice.final_price_in_words,
        items=[ItemResponse(
            reference=item.reference,
            quantity=item.quantity,
            designation=item.designation,
            unit_price=item.unit_price,
            total_price=float(f"{item.total_price:.3f}"),  # Round total_price for each item
        ) for item in items]
    )
    
    return invoice_detail_response
