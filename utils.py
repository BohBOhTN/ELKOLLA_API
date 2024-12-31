from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from models import Invoice
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
from openai import OpenAI
client = OpenAI()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

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
    number_formatted = "{:.3f}".format(number)
    
    try:
        # Create the chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"je vais te donner un montant en dinars en chiffre et tu dois me répondre juste avec le montant en lettres et donner moi aussi les millimes pas les centimes, le montant est {number_formatted}"
                }
            ],
            temperature=1,
            max_tokens=100,  # Use a reasonable max_tokens limit
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        # Access the content of the first choice
        words = response.choices[0].message.content
        return words
    
    except Exception as e:
        return f"Error: Unable to convert number to words. {str(e)}"