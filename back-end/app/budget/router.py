#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# router.py

"""
Description:
Author: Luis Maldonado.
Created on:
Modified on:
Version: 1.0.0
Dependencies:
"""
# ------------------------------------------- Libraries ----------------------------------------------------------
# Standard.
import locale
import os
from datetime import datetime
from typing import Annotated, cast

# Third-party.
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import ColumnElement
# noinspection PyUnresolvedReferences
from sqlalchemy.orm import Session
# from starlette import status
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from starlette import status
from starlette.responses import FileResponse

# Custom.
from budget.models import BudgetDB, BudgetItemDB
from budget.schemas import BudgetResponse, Budget
from utils.errors import DB_ERRORS
from utils.miscellaneous import get_db, log_out

# ------------------------------------------- Instances ----------------------------------------------------------
router = APIRouter(
    prefix='/budget',
    tags=['budgets']
)
db_dependency: type[Session] = Annotated[Session, Depends(get_db)]


# ------------------------------------------- Functions ----------------------------------------------------------
def header_footer(
        canv,
        doc
):
    canv.saveState()
    logo_width = 0
    if os.path.exists("img/logo.png"):
        logo_width = 100
        canv.drawImage("img/logo.png", 40, doc.pagesize[1] - 150, width=logo_width, height=150,
                       preserveAspectRatio=True, mask='auto')

    space_start = 10 + logo_width + 1
    available_space = doc.pagesize[0] - space_start - 60

    canv.setFont("Helvetica-Bold", 16)
    title = 'SOLUCIONES EN TODO TIPO DE ACABADOS "NECHA"'
    title_width = canv.stringWidth(title, "Helvetica-Bold", 14)
    x_center = space_start + (available_space - title_width) / 2
    canv.drawString(x_center, doc.pagesize[1] - 60, title)

    canv.setFont("Helvetica", 12)
    subtitle = "HÉCTOR NECHA MARTÍNEZ"
    subtitle_width = canv.stringWidth(subtitle, "Helvetica", 12)
    x_center_sub = space_start + (available_space - subtitle_width) / 2
    canv.drawString(x_center_sub, doc.pagesize[1] - 80, subtitle)
    canv.setFont("Helvetica", 9)
    footer_text = "Calle Clavel no. 183 Col Acampa Deleg. Cuauhtémoc C.P. 06450 México D.F.   Cel. 55 8554 8852"
    canv.drawString(40, 28, footer_text)
    page_num = canv.getPageNumber()
    canv.drawRightString(doc.pagesize[0] - 40, 28, f"Página {page_num}")
    canv.restoreState()


# ------------------------------------------- Routes ----------------------------------------------------------
@router.get(
    path=""
)
def get_budgets(
        db: db_dependency
):
    try:
        budgets = db.query(BudgetDB).order_by(BudgetDB.created_at.desc()).all()
        return budgets
    except DB_ERRORS as e:
        log_out(message=f'Error reading budgets. Cause - {e}')
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Error getting budgets from DB')
    finally:
        db.close()


@router.post(
    path="",
    response_model=BudgetResponse
)
def generate_budget(
        data: Budget,
        db: db_dependency
):
    try:
        os.makedirs("files", exist_ok=True)
        if data.company is None or data.company == ' ':
            company_safe = "".join(c if c.isalnum() else "_" for c in data.attention)
        else:
            company_safe = "".join(c if c.isalnum() else "_" for c in data.company)
        filename = f"presupuesto_{company_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = f"files/{filename}"

        # Calcular totales
        subtotal = sum(item.quantity * item.unit_price for item in data.items)
        tax = subtotal * 0.16
        total = subtotal + tax

        # Guardar en base de datos
        db_budget = BudgetDB(
            company=data.company,
            address=data.address,
            attention=data.attention,
            work_address=data.work_address,
            advance=data.advance,
            acceptance_text=data.acceptance_text,
            subtotal=float(subtotal),
            tax=float(tax),
            total=float(total),
            pdf_filename=filename
        )

        db.add(db_budget)
        db.flush()

        # Guardar items
        for idx, item in enumerate(data.items, start=1):
            amount = item.quantity * item.unit_price
            db_item = BudgetItemDB(
                budget_id=db_budget.id,
                item_number=idx,
                specifications=item.specifications,
                unit=item.unit,
                quantity=float(item.quantity),
                unit_price=float(item.unit_price),
                amount=float(amount)
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_budget)

        # Generar PDF
        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=120,
                                bottomMargin=40)
        elements = []
        styles = getSampleStyleSheet()
        header_gray = colors.HexColor("#D9D9D9")
        border_gray = colors.black
        total_width = letter[0] - (30 * 2)
        date_display = datetime.now().strftime("%d/%m/%Y")

        header_style = ParagraphStyle(
            name="HeaderStyle",
            fontName="Helvetica-Bold",
            fontSize=8,
            alignment=1
        )
        address_style = ParagraphStyle(
            name="WorkAddress",
            fontName="Helvetica",
            fontSize=10,
            leading=12,
        )

        general_data = [
            [f"Empresa: {data.company}", Paragraph("PRESUPUESTO", header_style)],
            [Paragraph(f"Dirección: {data.address}", address_style), ""],
            [f"Atención: {data.attention}", Paragraph("FECHA", header_style)],
            [Paragraph(f"Dirección de la Obra: {data.work_address}", address_style), date_display]
        ]

        general_col_widths = [total_width * 0.7, total_width * 0.3]
        general_table = Table(general_data, colWidths=general_col_widths)
        general_table.setStyle(TableStyle([
            ('BACKGROUND', (1, 0), (1, 0), header_gray),
            ('BACKGROUND', (1, 2), (1, 2), header_gray),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
            ('ALIGN', (1, 2), (1, 2), 'CENTER'),
            ('VALIGN', (1, 2), (1, 2), 'MIDDLE'),
            ('ALIGN', (1, 3), (1, 3), 'CENTER'),
            ('VALIGN', (1, 3), (1, 3), 'MIDDLE'),
            ('LINEABOVE', (0, 0), (0, 0), 1, border_gray),
            ('LINEBEFORE', (0, 0), (0, 0), 1, border_gray),
            ('LINEBEFORE', (0, 1), (0, 1), 1, border_gray),
            ('LINEBEFORE', (0, 2), (0, 2), 1, border_gray),
            ('LINEBELOW', (0, 2), (0, 2), 1, border_gray),
            ('LINEABOVE', (0, 3), (0, 3), 1, border_gray),
            ('LINEBELOW', (0, 3), (0, 3), 1, border_gray),
            ('LINEBEFORE', (0, 3), (0, 3), 1, border_gray),
            ('BOX', (1, 0), (1, 3), 1, border_gray),
            ('INNERGRID', (1, 0), (1, 3), 1, border_gray),
        ]))
        general_table.hAlign = 'CENTER'
        elements.append(general_table)
        elements.append(Spacer(1, 20))

        cell_style = styles["Normal"]
        cell_style.fontName = "Helvetica"
        cell_style.fontSize = 8

        items_header = [
            Paragraph("NO", header_style),
            Paragraph("ESPECIFICACIONES", header_style),
            Paragraph("UNIDAD", header_style),
            Paragraph("CANTIDAD", header_style),
            Paragraph("P.U.", header_style),
            Paragraph("IMPORTE", header_style)
        ]
        items_data = [items_header]

        for idx, item in enumerate(data.items, start=1):
            amount = item.quantity * item.unit_price
            quantity_str = str(int(item.quantity)) if item.quantity == int(item.quantity) else str(item.quantity)
            items_data.append([
                str(idx),
                Paragraph(item.specifications, cell_style),
                item.unit,
                quantity_str,
                locale.currency(item.unit_price, grouping=True),
                locale.currency(amount, grouping=True)
            ])

        proportions = [0.07, 0.43, 0.10, 0.12, 0.14, 0.14]
        items_col_widths = [total_width * p for p in proportions]

        items_table = Table(items_data, colWidths=items_col_widths, repeatRows=1)
        items_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, border_gray),
            ('BACKGROUND', (0, 0), (-1, 0), header_gray),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (3, -1), 'CENTER'),
            ('ALIGN', (4, 1), (5, -1), 'RIGHT'),
        ]))
        items_table.hAlign = 'CENTER'
        items_table.keepWithNext = True
        elements.append(items_table)
        elements.append(Spacer(1, 20))

        totals_data = [
            [Paragraph("SUBTOTAL", header_style), locale.currency(subtotal, grouping=True)],
            [Paragraph("I.V.A. 16%", header_style), locale.currency(tax, grouping=True)],
            [Paragraph("IMPORTE TOTAL", header_style), locale.currency(total, grouping=True)]
        ]

        separation_space = 20
        half_table_width = (total_width - separation_space) / 2

        totals_table = Table(totals_data, colWidths=[half_table_width * 0.5, half_table_width * 0.5])
        totals_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, border_gray),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (0, -1), header_gray),
        ]))

        payment_form = [
            [Paragraph("FORMA DE PAGO", header_style), ""],
            ["ANTICIPO", f"EL OTRO PAGO DEL {100 - data.advance}%"],
            [f"{data.advance}%", "En estimaciones semanales"]
        ]
        payment_table = Table(payment_form, colWidths=[half_table_width * 0.3, half_table_width * 0.7])
        payment_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, border_gray),
            ('BACKGROUND', (0, 0), (1, 0), header_gray),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (1, 0), 'MIDDLE'),
        ]))

        container = Table([[payment_table, "", totals_table]],
                          colWidths=[half_table_width, separation_space, half_table_width])
        container.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        container.hAlign = 'CENTER'
        container.keepWithNext = True
        elements.append(container)
        elements.append(Spacer(1, 20))

        signature_style = ParagraphStyle(name="SignatureStyle", fontName="Helvetica", fontSize=8, leading=12,
                                         alignment=1)

        signature_data = [
            [Paragraph("SOLUCIONES EN TODO TIPO DE", header_style),
             Paragraph("NOMBRE Y FIRMA DEL CLIENTE", header_style),
             Paragraph("OBSERVACIONES", header_style)],
            ["", "", ""],
            ["Héctor Necha Martínez", Paragraph(data.acceptance_text or "", signature_style), ""]
        ]

        signature_col_widths = [total_width / 3, total_width / 3, total_width / 3]
        signature_table = Table(signature_data, colWidths=signature_col_widths, rowHeights=[20, 60, None])
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), header_gray),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('NOSPLIT', (0, 0), (-1, -1)),
            ('GRID', (0, 0), (1, -1), 1, border_gray),
            ('LINEABOVE', (2, 0), (2, 0), 1, border_gray),
            ('LINEBELOW', (2, 0), (2, 0), 1, border_gray),
            ('LINEBEFORE', (2, 0), (2, -1), 1, border_gray),
            ('LINEAFTER', (2, 0), (2, -1), 1, border_gray),
            ('LINEBELOW', (2, -1), (2, -1), 1, border_gray),
        ]))
        signature_table.hAlign = 'CENTER'
        elements.append(signature_table)

        doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)

        return BudgetResponse(
            id=db_budget.id,
            company=db_budget.company,
            address=db_budget.address,
            attention=db_budget.attention,
            work_address=db_budget.work_address,
            advance=db_budget.advance,
            subtotal=float(db_budget.subtotal),
            tax=float(db_budget.tax),
            total=float(db_budget.total),
            pdf_filename=db_budget.pdf_filename,
            created_at=db_budget.created_at
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/{budget_id}")
def get_budget(
        budget_id: int,
        db: db_dependency
):
    try:
        budget = db.query(BudgetDB).filter(cast(ColumnElement[bool], BudgetDB.id == budget_id)).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

        # Crear respuesta con items incluidos
        response = {
            "id": budget.id,
            "company": budget.company,
            "address": budget.address,
            "attention": budget.attention,
            "work_address": budget.work_address,
            "advance": budget.advance,
            "acceptance_text": budget.acceptance_text,
            "subtotal": float(budget.subtotal),
            "tax": float(budget.tax),
            "total": float(budget.total),
            "pdf_filename": budget.pdf_filename,
            "created_at": budget.created_at,
            "items": [
                {
                    "id": item.id,
                    "budget_id": item.budget_id,
                    "item_number": item.item_number,
                    "specifications": item.specifications,
                    "unit": item.unit,
                    "quantity": float(item.quantity),
                    "unit_price": float(item.unit_price),
                    "amount": float(item.amount)
                }
                for item in sorted(budget.items, key=lambda x: x.item_number)
            ]
        }
        return response
    finally:
        db.close()


@router.get("/{budget_id}/pdf")
def download_budget(
        budget_id: int,
        db: db_dependency

):
    try:
        budget = db.query(BudgetDB).filter(cast(ColumnElement[bool], BudgetDB.id == budget_id)).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

        filepath = f"files/{budget.pdf_filename}"
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Archivo PDF no encontrado")

        return FileResponse(
            path=filepath,
            media_type="application/pdf",
            filename=budget.pdf_filename,
            headers={"Content-Disposition": f'attachment; filename="{budget.pdf_filename}"'}
        )
    finally:
        db.close()


@router.delete("/{budget_id}")
def delete_budget(
        budget_id: int,
        db: db_dependency
):
    try:
        budget = db.query(BudgetDB).filter(cast(ColumnElement[bool], BudgetDB.id == budget_id)).first()
        if not budget:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

        # Eliminar archivo PDF si existe
        filepath = f"files/{budget.pdf_filename}"
        if os.path.exists(filepath):
            os.remove(filepath)

        # Eliminar de base de datos
        db.delete(budget)
        db.commit()

        return {"message": "Presupuesto eliminado exitosamente"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# End-of-file (EOF)
