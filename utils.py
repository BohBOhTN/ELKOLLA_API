from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func  # Import func for SQL functions
from models import Invoice  # Import your Invoice model here
from num2words import num2words  # Library for converting numbers to words

def generate_invoice_number(invoice_date: str, db: Session) -> str:
    # Convert the provided invoice_date to datetime.date
    invoice_date_obj = datetime.strptime(invoice_date, "%d/%m/%Y").date()
    month = invoice_date_obj.month
    year = invoice_date_obj.year

    # Query the database for the last invoice in the same month and year
    last_invoice = (
        db.query(Invoice)
        .filter(
            func.extract('month', Invoice.invoice_date) == month,
            func.extract('year', Invoice.invoice_date) == year
        )
        .order_by(Invoice.invoice_number.desc())
        .first()
    )

    # Extract the last invoice number suffix or set it to 0 if no invoices exist
    if last_invoice:
        last_number = int(last_invoice.invoice_number.split('_')[-1])
    else:
        last_number = 0

    # Increment the last number by 1
    new_number = last_number + 1

    # Generate the new invoice number in the format MMYY_XXX
    month_year = f"{str(month).zfill(2)}{str(year)[-2:]}"  # MMYY
    return f"{month_year}_{str(new_number).zfill(3)}"

def number_to_words(number: float) -> str:
    """
    Convert a number to its French word representation, appending "Dinars."
    """
    words = num2words(number, lang="fr")  # Convert the number to French words
    return f"{words.capitalize()} dinars"
