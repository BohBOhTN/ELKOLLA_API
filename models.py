from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    invoice_id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String, unique=True, index=True)
    client_name = Column(String)
    vat_number = Column(String)
    address = Column(String)
    invoice_date = Column(Date)
    subtotal_ht = Column(Float)
    montant_tva = Column(Float)
    timbre_price = Column(Float)
    final_price = Column(Float)
    final_price_in_words = Column(String)

    items = relationship("Item", back_populates="invoice")

class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.invoice_id"))
    reference = Column(String)
    quantity = Column(Integer)
    designation = Column(String)
    unit_price = Column(Float)
    total_price = Column(Float)

    invoice = relationship("Invoice", back_populates="items")
