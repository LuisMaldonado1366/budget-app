#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# schemas.py

"""
Description:
Author: Luis Maldonado.
Created on:
Modified on:
Version: 1.0.0
Dependencies:
"""
# ------------------------------------------- Instances ----------------------------------------------------------
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


# ------------------------------------------- Classes ----------------------------------------------------------
class Item(BaseModel):
    specifications: str
    unit: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(gt=0)


class Budget(BaseModel):
    company: str | None = None
    address: str | None = None
    attention: str | None = None
    work_address: str | None = None
    items: List[Item] | None = None
    advance: int | None = None
    acceptance_text: str | None = "Acepto(amos) y autorizo(amos) para su realización"


class BudgetResponse(BaseModel):
    id: int
    company: str | None
    address: str | None
    attention: str | None
    work_address: str | None
    advance: int | None
    subtotal: float
    tax: float
    total: float
    pdf_filename: str
    created_at: datetime

    class Config:
        from_attributes = True

# End-of-file (EOF)
