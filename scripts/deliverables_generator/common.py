"""Common styling, formatting, and PDF canvas utilities for CRBCL deliverables."""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

PRIMARY_HEX = "#6B1D2F"      # Burgundy / Maroon
SECONDARY_HEX = "#C98A2C"    # Ochre Gold
DARK_HEX = "#1E293B"         # Charcoal / Navy
LIGHT_BG_HEX = "#F8FAFC"     # Off-white / light slate
BORDER_HEX = "#CBD5E1"       # Light border grey
MUTED_HEX = "#64748B"        # Slate grey

COLOR_PRIMARY = colors.HexColor(PRIMARY_HEX)
COLOR_SECONDARY = colors.HexColor(SECONDARY_HEX)
COLOR_DARK = colors.HexColor(DARK_HEX)
COLOR_LIGHT_BG = colors.HexColor(LIGHT_BG_HEX)
COLOR_BORDER = colors.HexColor(BORDER_HEX)
COLOR_MUTED = colors.HexColor(MUTED_HEX)

DELIVERABLES_DIR = r"C:\Users\Shilley Pc\crbcl\deliverables\CRBCL_Board_Update_October_2026"
os.makedirs(DELIVERABLES_DIR, exist_ok=True)


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count 'Page X of Y'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(COLOR_MUTED)

            # Running Header
            self.drawString(54, 750, "CHIEF RED BEAR CHILDREN'S LODGE — BOARD & TECHNICAL REPORT (OCTOBER 2026)")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

            # Running Footer
            self.line(54, 45, 558, 45)
            self.drawString(54, 32, "CONFIDENTIAL — STRICTLY FOR CRBCL LEADERSHIP & BOARD REVIEW")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 32, page_text)
            self.restoreState()


def get_pdf_styles():
    """Build and return custom ReportLab styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CRBCL_DocTitle",
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=COLOR_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=12,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_DocSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=20,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_MetaText",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=COLOR_MUTED,
        alignment=TA_CENTER,
        spaceAfter=25,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_H1",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=COLOR_PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_H2",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=COLOR_DARK,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_H3",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=COLOR_SECONDARY,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_Body",
        fontName="Helvetica",
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_DARK,
        spaceAfter=7,
        alignment=TA_JUSTIFY,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_BodyBold",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13.5,
        textColor=COLOR_DARK,
        spaceAfter=7,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_NoticeBox",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#78350F"),  # dark amber
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_NoticeTitle",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#92400E"),  # bold amber
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=COLOR_DARK,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=COLOR_DARK,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white,
        alignment=TA_CENTER,
    ))

    return styles


def create_pdf_notice_box(title, text, styles):
    """Create a high-visibility callout box for mandatory notices."""
    content = [
        Paragraph(f"⚠️ {title}", styles["CRBCL_NoticeTitle"]),
        Paragraph(text, styles["CRBCL_NoticeBox"]),
    ]
    t = Table([[content]], colWidths=[504])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),  # light amber
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#F59E0B")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def set_cell_background(cell, fill_hex):
    """Set background color on a docx cell using XML."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding on a docx table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)
