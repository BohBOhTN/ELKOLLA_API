from fastapi.encoders import jsonable_encoder  # Fix: Add this line
from sqlalchemy.orm import Session
from models import Invoice, Item
from database import SessionLocal, init_db
from pydantic import BaseModel
from utils import number_to_words, generate_invoice_number  # Import the helper function
from datetime import datetime
from typing import List, Optional
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.sql import func  # Import func for SQL functions
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Initialize the database
init_db()

# Allow all origins for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8123"],  # You can restrict this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods, including OPTIONS
    allow_headers=["*"],  # Allows all headers
)

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

class InvoiceResponse(BaseModel):
    invoice_number: str
    subtotal_ht: float
    montant_tva: float
    timbre_price: float
    final_price: float
    final_price_in_words: str

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

    # 3. Fixed Timbre price (1 dinar)
    timbre_price = 1.0

    # 4. Final price
    final_price = subtotal_ht + montant_tva + timbre_price

    # 5. Generate invoice number (MMYY_XXX)
    invoice_number = generate_invoice_number(invoice_request.invoice_date, db)

    # 6. Convert final price to words
    final_price_in_words = number_to_words(final_price)

    # 7. Create invoice record in the database
    invoice = Invoice(
        client_name=invoice_request.client_name,
        vat_number=invoice_request.vat_number,
        address=invoice_request.address,
        invoice_date=invoice_date_obj,  # Use the converted date object here
        invoice_number=invoice_number,
        subtotal_ht=subtotal_ht,
        montant_tva=montant_tva,
        timbre_price=timbre_price,
        final_price=final_price,
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
            total_price=item.unit_price * item.quantity
        )
        db.add(db_item)
    
    db.commit()

    return InvoiceResponse(
        invoice_number=invoice_number,
        subtotal_ht=subtotal_ht,
        montant_tva=montant_tva,
        timbre_price=timbre_price,
        final_price=final_price,
        final_price_in_words=final_price_in_words
    )

@app.get("/invoices", response_model=List[InvoiceResponse])
def get_invoices(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve invoices filtered by year, month, or day.
    - year: Optional[int] -> Filter by year
    - month: Optional[int] -> Filter by month
    - day: Optional[int] -> Filter by day
    """
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
            subtotal_ht=invoice.subtotal_ht,
            montant_tva=invoice.montant_tva,
            timbre_price=invoice.timbre_price,
            final_price=invoice.final_price,
            final_price_in_words=invoice.final_price_in_words,
        )
        for invoice in invoices
    ]

    # Use jsonable_encoder to serialize Pydantic models
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


