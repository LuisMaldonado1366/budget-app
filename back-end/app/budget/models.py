#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# models.py

"""
Description:
Author: Luis Maldonado.
Created on:
Modified on:
Version: 1.0.0
Dependencies:
"""
# ------------------------------------------- Libraries ----------------------------------------------------------
# Third-party
from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

# Custom
from utils.database import Base


# ------------------------------------------- Classes ----------------------------------------------------------
# Modelos de base de datos
class BudgetDB(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String(255))
    address = Column(Text)
    attention = Column(String(255))
    work_address = Column(Text)
    advance = Column(Integer)
    acceptance_text = Column(Text)
    subtotal = Column(DECIMAL(10, 2))
    tax = Column(DECIMAL(10, 2))
    total = Column(DECIMAL(10, 2))
    pdf_filename = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())

    items = relationship("BudgetItemDB", back_populates="budget", cascade="all, delete-orphan")


class BudgetItemDB(Base):
    __tablename__ = "budget_items"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id"), nullable=False)
    item_number = Column(Integer, nullable=False)
    specifications = Column(Text, nullable=False)
    unit = Column(String(50), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)

    budget = relationship("BudgetDB", back_populates="items")

# End-of-file (EOF)
