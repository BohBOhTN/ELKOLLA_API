
# ELKOLLA API

## Project Overview
The ELKOLLA API is a FastAPI-based web service designed for managing invoices, including their creation, retrieval, and deletion. It uses SQLAlchemy for ORM-based database management and integrates utility functions for invoice number generation and converting numeric amounts to words in French. The project provides endpoints to generate invoices, list them based on various filters, and delete them when necessary.

## Features

- **Invoice Creation**: Allows users to create invoices by providing client details, invoice date, and items with quantity and unit price.
- **Invoice Retrieval**: Fetches invoices filtered by year, month, and day.
- **Invoice Deletion**: Deletes invoices by either invoice ID or invoice number, along with their associated items.
- **Dynamic Invoice Number Generation**: Invoice numbers are automatically generated in the format `MMYY_XXX` based on the current month and year.
- **Amount Conversion**: Converts the final price of invoices into words using OpenAI's GPT model, specifically for French numbers.
- **Database Support**: Uses SQLAlchemy ORM for storing invoices and associated items in a PostgreSQL database hosted on AWS RDS.

## Technology Stack
- **FastAPI**: Framework for building the API endpoints.
- **SQLAlchemy**: ORM for database interaction.
- **PostgreSQL on AWS RDS**: Database used for storage.
- **OpenAI GPT-3**: Used for converting numeric amounts into French words.
- **Pydantic**: For data validation and serialization.
- **JavaScript / Flatpickr**: For front-end validation, including calendar-based date input and user-friendly item management.

## API Endpoints

### 1. **Create Invoice**
- **Endpoint**: `/create_invoice`
- **Method**: POST
- **Description**: Creates an invoice with details such as client information, items, and calculates total amounts, including VAT and timbre price.
- **Request Body**:
  ```json
  {
    "client_name": "John Doe",
    "vat_number": "123456789",
    "address": "123 Main St, City, Country",
    "invoice_date": "31/12/2024",
    "items": [
      {
        "reference": "item001",
        "quantity": 2,
        "designation": "Product A",
        "unit_price": 15.0
      },
      {
        "reference": "item002",
        "quantity": 1,
        "designation": "Product B",
        "unit_price": 25.0
      }
    ]
  }
  ```

- **Response**:
  ```json
  {
    "invoice_number": "1234_001",
    "subtotal_ht": 55.0,
    "montant_tva": 3.85,
    "timbre_price": 1.0,
    "final_price": 59.85,
    "final_price_in_words": "Fifty-nine dinars and eighty-five millimes"
  }
  ```

### 2. **Get Invoices**
- **Endpoint**: `/invoices`
- **Method**: GET
- **Description**: Retrieves invoices, filtered by year, month, or day.
- **Query Parameters**:
  - `year`: Optional filter by year.
  - `month`: Optional filter by month.
  - `day`: Optional filter by day.
- **Response**:
  ```json
  [
    {
      "invoice_number": "1234_001",
      "subtotal_ht": 55.0,
      "montant_tva": 3.85,
      "timbre_price": 1.0,
      "final_price": 59.85,
      "final_price_in_words": "Fifty-nine dinars and eighty-five millimes"
    }
  ]
  ```

### 3. **Delete Invoice**
- **Endpoint**: `/delete_invoice`
- **Method**: DELETE
- **Description**: Deletes an invoice by its ID or invoice number along with its associated items.
- **Query Parameters**:
  - `invoice_id`: The ID of the invoice to be deleted.
  - `invoice_number`: The number of the invoice to be deleted.
- **Response**:
  ```json
  {
    "message": "Invoice has been deleted successfully."
  }
  ```

## Database Models

### Invoice
- `invoice_id`: Integer (Primary Key)
- `invoice_number`: String (Unique)
- `client_name`: String
- `vat_number`: String
- `address`: String
- `invoice_date`: Date
- `subtotal_ht`: Float
- `montant_tva`: Float
- `timbre_price`: Float
- `final_price`: Float
- `final_price_in_words`: String

### Item
- `item_id`: Integer (Primary Key)
- `invoice_id`: Integer (Foreign Key to Invoice)
- `reference`: String
- `quantity`: Integer
- `designation`: String
- `unit_price`: Float
- `total_price`: Float

## Utility Functions

- **generate_invoice_number**: Generates a unique invoice number based on the current month and year, following the format MMYY_XXX. It increments the suffix for each new invoice created within the same month and year.
- **number_to_words**: Converts a numeric amount (e.g., 59.85) into words (e.g., "Fifty-nine dinars and eighty-five millimes") using OpenAI's GPT-3 API.

## Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required for number-to-words conversion).

## Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/BohBOhTN/ELKOLLA_API.git
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add your OpenAI API key:

     ```makefile
     OPENAI_API_KEY=your_api_key
     ```

4. Run the FastAPI app:

   ```bash
   uvicorn main:app --reload
   ```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).
