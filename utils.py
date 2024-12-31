from datetime import datetime
from sqlalchemy.orm import Session
from models import Invoice  # Import your Invoice model here

def generate_invoice_number(invoice_date: str, db: Session) -> str:
    # Logic to generate the invoice number (MMYY_XXX)
    month_year = invoice_date[3:5] + invoice_date[8:10]  # MMYY
    count = db.query(Invoice).filter(Invoice.invoice_date.startswith(month_year)).count()
    return f"{month_year}_{str(count + 1).zfill(3)}"

# Placeholder function for converting numbers to words
def number_to_words(number: float) -> str:
    # Simple placeholder for converting number to words (you can use a library for more complex conversion)
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten"]
    return f"{units[int(number)]} Dinars" if number < 11 else f"{number} Dinars"
