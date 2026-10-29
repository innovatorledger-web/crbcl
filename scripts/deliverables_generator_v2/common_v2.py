"""Common styling, formatting, and canvas utilities for CRBCL Revision 2 deliverables."""

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
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

PRIMARY_HEX = "#6B1D2F"      # Burgundy / Maroon (CRBCL Primary)
SECONDARY_HEX = "#C98A2C"    # Ochre Gold (CRBCL Secondary)
DARK_HEX = "#1E293B"         # Charcoal / Navy Slate
LIGHT_BG_HEX = "#F8FAFC"     # Off-white / light slate
BORDER_HEX = "#CBD5E1"       # Light border grey
MUTED_HEX = "#64748B"        # Slate grey
AMBER_BG_HEX = "#FEF3C7"     # Warning notice light amber
AMBER_BORDER_HEX = "#F59E0B" # Warning notice border

COLOR_PRIMARY = colors.HexColor(PRIMARY_HEX)
COLOR_SECONDARY = colors.HexColor(SECONDARY_HEX)
COLOR_DARK = colors.HexColor(DARK_HEX)
COLOR_LIGHT_BG = colors.HexColor(LIGHT_BG_HEX)
COLOR_BORDER = colors.HexColor(BORDER_HEX)
COLOR_MUTED = colors.HexColor(MUTED_HEX)

DELIVERABLES_V2_DIR = r"C:\Users\Shilley Pc\crbcl\deliverables\CRBCL_Board_Update_October_2026\Revision_2"
PRIVATE_COMMERCIAL_DIR = os.path.join(DELIVERABLES_V2_DIR, "Private_Commercial")
BOARD_DISTRIBUTION_DIR = os.path.join(DELIVERABLES_V2_DIR, "Board_Distribution_Package")
PRIVATE_COMMERCIAL_PACKAGE_DIR = r"C:\Users\Shilley Pc\crbcl\deliverables\CRBCL_Private_Developer_Commercial_Correspondence_October_2026"

os.makedirs(DELIVERABLES_V2_DIR, exist_ok=True)
os.makedirs(PRIVATE_COMMERCIAL_DIR, exist_ok=True)
os.makedirs(BOARD_DISTRIBUTION_DIR, exist_ok=True)
os.makedirs(PRIVATE_COMMERCIAL_PACKAGE_DIR, exist_ok=True)


class NumberedCanvasPrivate(canvas.Canvas):
    """Two-pass canvas for Private Developer Commercial Correspondence."""

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
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(COLOR_MUTED)

            # Running Header
            header_text = "PRIVATE & CONFIDENTIAL — FOR THE ORIGINAL HIRING CONTACT ONLY"
            self.drawString(54, 752, header_text)
            self.setFont("Helvetica", 8)
            self.drawRightString(558, 752, "OCTOBER 2026")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(54, 746, 558, 746)

            # Running Footer
            self.line(54, 45, 558, 45)
            footer_text = "CONFIDENTIAL COMMERCIAL CORRESPONDENCE — NOT FOR BOARD DISTRIBUTION"
            self.drawString(54, 32, footer_text)
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 32, page_text)
            self.restoreState()


class NumberedCanvasV2(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count 'Page X of Y'."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.doc_title = "CHIEF RED BEAR CHILDREN'S LODGE — BOARD & TECHNICAL REPORT (REVISION 2)"

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
        # Omit header and footer on cover page (Page 1)
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(COLOR_MUTED)

            # Running Header
            header_text = getattr(self, "doc_header_text", "CHIEF RED BEAR CHILDREN'S LODGE — REVISION 2 (OCTOBER 2026)")
            self.drawString(54, 752, header_text)
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(54, 746, 558, 746)

            # Running Footer
            self.line(54, 45, 558, 45)
            footer_text = getattr(self, "doc_footer_text", "CONFIDENTIAL — STRICTLY FOR CRBCL LEADERSHIP & AUTHORIZED AUDITORS")
            self.drawString(54, 32, footer_text)
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 32, page_text)
            self.restoreState()


def get_pdf_styles_v2():
    """Build and return custom ReportLab styles for Revision 2."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="CRBCL_CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=28,
        textColor=COLOR_PRIMARY,
        alignment=TA_CENTER,
        spaceAfter=14,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_CoverSubtitle",
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        alignment=TA_CENTER,
        spaceAfter=20,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_CoverMeta",
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=COLOR_DARK,
        alignment=TA_CENTER,
        spaceAfter=24,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_H1",
        fontName="Helvetica-Bold",
        fontSize=13.5,
        leading=17,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_H2",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=COLOR_DARK,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_H3",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=13,
        textColor=COLOR_SECONDARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_Body",
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=COLOR_DARK,
        spaceAfter=5.5,
        alignment=TA_JUSTIFY,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_BodyBold",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=COLOR_DARK,
        spaceAfter=5.5,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_NoticeBox",
        fontName="Helvetica",
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor("#78350F"),  # dark amber
        spaceAfter=4,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_NoticeTitle",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#92400E"),  # bold amber
        spaceAfter=3,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_TableCell",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=COLOR_DARK,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=COLOR_DARK,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10.5,
        textColor=colors.white,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="CRBCL_DiagramText",
        fontName="Courier",
        fontSize=7,
        leading=8.5,
        textColor=COLOR_DARK,
    ))

    return styles


def create_pdf_notice_box_v2(title, text, styles):
    """Create a high-visibility callout box for mandatory notices in Revision 2."""
    content = [
        Paragraph(f"⚠️ {title}", styles["CRBCL_NoticeTitle"]),
        Paragraph(text, styles["CRBCL_NoticeBox"]),
    ]
    t = Table([[content]], colWidths=[504])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(AMBER_BG_HEX)),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(AMBER_BORDER_HEX)),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def create_pdf_diagram_box(ascii_diagram_text, styles, width=504):
    """Format and wrap an ASCII architecture diagram into a clean border box."""
    p = Preformatted(ascii_diagram_text, styles["CRBCL_DiagramText"])
    t = Table([[p]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("BOX", (0, 0), (-1, -1), 0.75, colors.HexColor(BORDER_HEX)),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def set_cell_background(cell, fill_hex):
    """Set background color on a docx cell using XML."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, left=100, right=100):
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
