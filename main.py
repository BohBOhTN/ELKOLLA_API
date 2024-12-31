from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from models import Invoice, Item
from database import SessionLocal, init_db
from pydantic import BaseModel
from utils import number_to_words, generate_invoice_number  # Import the helper function

app = FastAPI()

# Initialize the database
init_db()

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
        invoice_date=invoice_request.invoice_date,
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