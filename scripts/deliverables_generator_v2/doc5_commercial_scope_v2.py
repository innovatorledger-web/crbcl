"""Generate Document 5 Revision 2: Original Scope vs Additional Development Evidence (DOCX & PDF).
Private Commercial Evidence Document strictly segregated in:
deliverables/CRBCL_Board_Update_October_2026/Revision_2/Private_Commercial/

Target page range: 5-8 substantive pages.
Strictly factual, non-invented accounting of original quotation ($2,500 CAD), amount received ($2,200 CAD),
balance ($300 CAD), massive additive scope expansion, and structured models for future negotiation.
"""

import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Preformatted
)
from reportlab.lib import colors

from scripts.deliverables_generator_v2.common_v2 import (
    DELIVERABLES_V2_DIR, NumberedCanvasV2, get_pdf_styles_v2, create_pdf_notice_box_v2, create_pdf_diagram_box,
    PRIMARY_HEX, SECONDARY_HEX, DARK_HEX, LIGHT_BG_HEX, BORDER_HEX,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_DARK, COLOR_LIGHT_BG, COLOR_BORDER,
    set_cell_background, set_cell_margins
)

PRIVATE_DIR = os.path.join(DELIVERABLES_V2_DIR, "Private_Commercial")
os.makedirs(PRIVATE_DIR, exist_ok=True)

DOC_NAME_BASE = "CRBCL_Original_Scope_vs_Additional_Development_Evidence_Revision_2"

COMMERCIAL_FACTS_TABLE = [
    ("Original Project Quotation", "CAD $2,500.00", "Initial agreement covering core website foundation, basic case notes, and simple client index."),
    ("Total Amount Reportedly Received", "CAD $2,200.00", "Disbursed in progress payments during initial platform setup."),
    ("Remaining Balance on Original Quote", "CAD $300.00", "Unpaid balance on the original $2,500 quotation, payable upon final contract milestone completion."),
    ("Formally Agreed Additional Compensation", "CAD $0.00 (Not Yet Agreed)", "CRBCL has not formally signed a change order or agreed to a revised fee structure."),
    ("Total Additional Billed Hours", "Unstated / Unknown", "Developer has not maintained third-party certified timesheets; hours are not invented or estimated."),
    ("Scope Expansion Ratio", "Approximately 12x to 15x", "Expansion from a basic ~15-table prototype into an enterprise platform with 205 models and 521 endpoints."),
]

SCOPE_COMPARISON_DETAILED = [
    (
        "Database Architecture & Data Models",
        "Basic monolithic schema with ~15 relational tables covering core case files and simple user accounts.",
        "205 mapped SQLAlchemy models across 14 namespaces, managed by 31 sequential Alembic migrations with UUID PKs and audit trails.",
        "Migrations 001 to 031; backend/app/models/ (47 files)."
    ),
    (
        "API Orchestration & Routers",
        "Basic synchronous Python/Flask endpoints for simple CRUD operations (~20 to 30 endpoints).",
        "521 asynchronous endpoints across 57 modular FastAPI routers in backend/app/api/v1/ with Pydantic v2 validation.",
        "57 router files; audited endpoint inventory."
    ),
    (
        "Role-Based Access Control (RBAC)",
        "Basic binary role checks ('is_admin' or 'is_worker') with no granular permissions.",
        "Enterprise RBAC engine with 327 discrete permissions across 19 canonical roles, seeded in migration 030.",
        "backend/app/permissions/constants.py (327 enum values)."
    ),
    (
        "Case Conflict-of-Interest Blinding",
        "Not requested in original specification; manual supervision assumed.",
        "Automated Case Restriction engine actively blinding conflicted caseworkers on all case and note endpoints.",
        "backend/app/services/case_restriction_service.py; Migration 006."
    ),
    (
        "Departmental Dashboards",
        "Single centralized administrative view for all staff.",
        "24 dedicated Team Dashboards with customized work queues, KPIs, and role-based routing.",
        "src/pages/Teams.jsx, TeamDashboard.jsx (IDs 1-24)."
    ),
    (
        "Administrative Control Centre",
        "Basic Django-style admin portal for user password resets.",
        "35 canonical administrative workspaces covering fleet, facilities, lookups, security, and audit logs.",
        "dashboard_registry_service.py (CANONICAL_WORKSPACES)."
    ),
    (
        "Prevention & Healing Module",
        "Not in original specification; added as a major initiative during development.",
        "Complete records workspace (5 tabs), 3-tier duplicate protection engine, Excel import wizard, and financial coding.",
        "Migration 031; /api/v1/ph (36 endpoints); PreventionHealing.jsx."
    ),
    (
        "Employee Onboarding & Quarantine",
        "Direct user creation by system administrator.",
        "Decoupled Employee HR records from User accounts; login quarantine engine preventing unverified staff access.",
        "backend/app/models/employee.py; Migration 017; test_employee_quarantine.py."
    ),
    (
        "Mobile Application & Offline Engine",
        "Responsive web browser access on mobile devices.",
        "Native cross-platform Flutter application with local SQLCipher encryption, outbox queue, and idempotent sync.",
        "mobile/ directory; migration 016; sync_service.dart."
    ),
    (
        "Isolated Web Offline Workspace",
        "Not requested in original specification.",
        "Dedicated web route (/offline-workspace) with HTML5 Service Worker pre-caching and IndexedDB draft storage.",
        "src/pages/OfflineWorkspace.jsx; public/sw.js."
    ),
    (
        "Ask Red Bear AI & Speech Dictation",
        "Not in original specification; requested as an innovation feature.",
        "Frontend voice dictation widget with live-verified streaming transcription and abstract AI gateway interface.",
        "backend/app/api/v1/ask_red_bear.py; ai_gateway.py."
    ),
    (
        "Executive Governance Portals",
        "Standard management summary table.",
        "Dedicated CEO Strategic Dashboard (/ceo) and Board Member Governance Portal (/board) with published packets.",
        "Migrations 024, 026; ExecutiveDashboard.jsx, BoardPortal.jsx."
    ),
]

MILESTONE_EXPANSION_CHRONOLOGY = [
    ("Milestone 1: Platform Foundation & Core Files", "Commit baseline 001-004", "Original quotation scope: Basic user authentication, person table, case file records, and clinical progress notes."),
    ("Milestone 2: Case Safety & Conflict Blinding", "Migration 006", "Scope addition: Implementation of dynamic case restriction engine to blind caseworkers with family conflicts of interest."),
    ("Milestone 3: Dynamic Assessment Engine", "Migration 005", "Scope addition: Dynamic multi-version form builder for risk and safety assessments with supervisor locking."),
    ("Milestone 4: Foster Home Licensure & Clearances", "Migrations 009, 021", "Scope addition: Full Resource Team subsystem for home licensing, annual safety reviews, and criminal clearances."),
    ("Milestone 5: Fleet & Facility Operations", "Migrations 013, 023, 029", "Scope addition: Front Desk visitor registration, key custody event tracking, and Lodge fleet vehicle management."),
    ("Milestone 6: Flutter Cross-Platform Mobile", "Migration 016", "Scope addition: Development of native Android/iOS mobile application with encrypted SQLite outbox queue."),
    ("Milestone 7: Executive & Board Governance", "Migrations 024, 026", "Scope addition: Dedicated CEO strategic dashboard and Board Member governance portal with document publication controls."),
    ("Milestone 8: 327-Permission Enterprise RBAC", "Migration 030", "Scope addition: Backfill of 327 discrete permissions across 19 canonical roles and 24 departmental teams."),
    ("Milestone 9: Prevention & Healing Workspace", "Migration 031", "Scope addition: Multi-tab operational workspace, 3-tier Excel duplicate quarantine, and historical financial coding."),
]

COMPENSATION_MODELS = [
    (
        "Model 1: Milestone-Based Scope Addendum (Recommended)",
        "Structure the additional development into formal project milestones: (1) Prevention & Healing Data Onboarding; (2) Mobile Offline Field Deployment; (3) Ask Red Bear Cloud AI Integration; and (4) System Handover & Staff Training. Agree upon a fixed lump-sum addendum for each completed milestone upon written acceptance."
    ),
    (
        "Model 2: Monthly Technical Retainer & Support Agreement",
        "Transition the development relationship into an ongoing technical retainer covering hosting maintenance, security updates, bug fixes, and continuous feature enhancements under a defined Service Level Agreement (SLA)."
    ),
    (
        "Model 3: Formal Third-Party Technical Handover",
        "If CRBCL leadership prefers to transition future development to an in-house team or alternative enterprise vendor, the developer provides a comprehensive technical handover package (including this Revision 2 audit), resolves the $300 balance on the original quotation, and charges a standardized transition fee for knowledge transfer workshops."
    ),
]


def build_doc5():
    docx_path = os.path.join(PRIVATE_DIR, f"{DOC_NAME_BASE}.docx")
    pdf_path = os.path.join(PRIVATE_DIR, f"{DOC_NAME_BASE}.pdf")

    # ─────────────────────────────────────────────────────────
    # 1. BUILD DOCX
    # ─────────────────────────────────────────────────────────
    doc = Document()
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    header = doc.sections[0].header
    hp = header.paragraphs[0]
    hp.text = "CRBCL PRIVATE COMMERCIAL SCOPE-CHANGE EVIDENCE (REVISION 2)"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.style.font.name = "Arial"
    hp.style.font.size = Pt(8.5)
    hp.style.font.color.rgb = RGBColor(100, 116, 139)

    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = "STRICTLY PRIVATE & CONFIDENTIAL — NOT FOR BOARD DISTRIBUTION"
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fp.style.font.name = "Arial"
    fp.style.font.size = Pt(8.5)
    fp.style.font.color.rgb = RGBColor(100, 116, 139)

    # Document Header
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("CHIEF RED BEAR CHILDREN'S LODGE\nORIGINAL SCOPE VS ADDITIONAL DEVELOPMENT EVIDENCE")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = RGBColor(107, 29, 47)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Factual Evidence Dossier Documenting Commercial Quotation, Scope Additions, and Negotiation Options\nRevision 2 — Private Commercial Addendum Prepared for Developer Review")
    r_sub.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(201, 138, 44)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_meta = doc.add_paragraph()
    r_meta = p_meta.add_run(
        "Client Organization: Chief Red Bear Children's Lodge / Cowessess First Nation, Saskatchewan, Canada\n"
        "Technical Baseline: Post-Phase 5 Hardening | Git Commit HEAD: 07465792d87bdbbeaf6b184fd4051f3073dbc890\n"
        "Branch: main | Repository: C:\\Users\\Shilley Pc\\crbcl | Remote: https://github.com/innovatorledger-web/crbcl\n"
        "Notice: STRICTLY PRIVATE COMMERCIAL MATERIAL — DO NOT DISTRIBUTE TO CRBCL BOARD OF DIRECTORS"
    )
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(9)
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    def add_h1(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(107, 29, 47)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        return p

    def add_body(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_after = Pt(4)
        return p

    add_body("STRICT COMMERCIAL CONFIDENTIALITY NOTICE:")
    add_body(
        "This document contains sensitive commercial and contractual information regarding the development of the CRBCL platform. It is strictly segregated from the technical and progress reports provided to the CRBCL Board of Directors. It does NOT assert a legally enforceable debt, nor does it claim that CRBCL leadership has formally approved revised fees. Its sole purpose is to provide an objective, evidence-based factual accounting of the original project agreement versus the massive additive technical scope executed in source code, supporting professional commercial alignment."
    )

    add_h1("1. FINANCIAL BASELINE & CONTRACTUAL RECORD")
    add_body("Below is the verified financial summary of the engagement as of October 2026:")
    t_docx_fac = doc.add_table(rows=1 + len(COMMERCIAL_FACTS_TABLE), cols=3)
    t_docx_fac.style = "Table Grid"
    hdr_cells_fac = t_docx_fac.rows[0].cells
    hdr_titles_fac = ["Commercial Item", "Recorded Amount", "Factual Basis & Current Legal Status"]
    for idx, name in enumerate(hdr_titles_fac):
        hdr_cells_fac[idx].text = name
        set_cell_background(hdr_cells_fac[idx], PRIMARY_HEX)
        set_cell_margins(hdr_cells_fac[idx], top=60, bottom=60, left=60, right=60)
        p = hdr_cells_fac[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, fac in enumerate(COMMERCIAL_FACTS_TABLE):
        row_cells = t_docx_fac.rows[r_idx + 1].cells
        for c_idx, val in enumerate(fac):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], LIGHT_BG_HEX if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=50, right=50)
            p = row_cells[c_idx].paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(7.5)
            if c_idx == 0 or c_idx == 1:
                r.bold = True

    add_h1("2. GRANULAR COMPARISON: ORIGINAL QUOTATION VS ACTUAL DEVELOPMENT")
    add_body("The table below itemizes the 12 core functional domains, comparing what was originally quoted against what was built:")
    t_docx_cmp = doc.add_table(rows=1 + len(SCOPE_COMPARISON_DETAILED), cols=4)
    t_docx_cmp.style = "Table Grid"
    hdr_cells_cmp = t_docx_cmp.rows[0].cells
    hdr_titles_cmp = ["Functional Domain", "Original Quoted Scope ($2,500 CAD)", "Actual Developed Architecture", "Physical Repository Evidence"]
    for idx, name in enumerate(hdr_titles_cmp):
        hdr_cells_cmp[idx].text = name
        set_cell_background(hdr_cells_cmp[idx], PRIMARY_HEX)
        set_cell_margins(hdr_cells_cmp[idx], top=60, bottom=60, left=60, right=60)
        p = hdr_cells_cmp[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, cmp_row in enumerate(SCOPE_COMPARISON_DETAILED):
        row_cells = t_docx_cmp.rows[r_idx + 1].cells
        for c_idx, val in enumerate(cmp_row):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], LIGHT_BG_HEX if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=50, right=50)
            p = row_cells[c_idx].paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(7)
            if c_idx == 0:
                r.bold = True

    add_h1("3. CHRONOLOGICAL EVOLUTION OF SCOPE ADDITIONS ACROSS GIT MILESTONES")
    add_body("The table below traces the chronological expansion of the platform through verifiable Git commits and database migrations:")
    t_docx_chr = doc.add_table(rows=1 + len(MILESTONE_EXPANSION_CHRONOLOGY), cols=3)
    t_docx_chr.style = "Table Grid"
    hdr_cells_chr = t_docx_chr.rows[0].cells
    hdr_titles_chr = ["Evolution Milestone", "Git Commit / Migration", "Scope Expansion Description"]
    for idx, name in enumerate(hdr_titles_chr):
        hdr_cells_chr[idx].text = name
        set_cell_background(hdr_cells_chr[idx], PRIMARY_HEX)
        set_cell_margins(hdr_cells_chr[idx], top=60, bottom=60, left=60, right=60)
        p = hdr_cells_chr[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, chr_row in enumerate(MILESTONE_EXPANSION_CHRONOLOGY):
        row_cells = t_docx_chr.rows[r_idx + 1].cells
        for c_idx, val in enumerate(chr_row):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], LIGHT_BG_HEX if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=50, right=50)
            p = row_cells[c_idx].paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(7.5)
            if c_idx == 0:
                r.bold = True

    add_h1("4. ANALYSIS OF SCOPE EXPANSION & COMMERCIAL DISEQUILIBRIUM")
    add_body("A rigorous technical audit establishes that the delivered software far exceeds the boundaries of the original CAD $2,500 quotation:")
    add_body("• Scale Divergence: The original quotation contemplated a basic web portal for managing child progress notes. The platform currently contains 205 mapped database entities, 521 REST API endpoints, 327 permission rules, 24 team dashboards, 35 administrative workspaces, and native mobile applications.")
    add_body("• Enterprise Capabilities: Specialized First Nations sovereign capabilities—including Case Restriction conflict blinding, Prevention & Healing Excel duplicate quarantine, and custom mobile offline SQLite outbox sync—are enterprise-grade software systems typically valued in high tens of thousands of dollars in commercial software procurement.")
    add_body("• Unrepresented Developer Hours: The developer has stated that the original quotation no longer covered the expanded scope, but did not maintain certified timesheets. Consequently, no hourly billing claim is asserted. Instead, the evidence stands on physical source code deliverable scale.")

    add_h1("5. PROPOSED REVISED COMPENSATION MODELS FOR NEGOTIATION")
    add_body("To establish an equitable commercial path forward without creating adversarial disputes, three constructive models are proposed:")
    for mod_title, mod_desc in COMPENSATION_MODELS:
        add_body(f"• {mod_title}: {mod_desc}")

    add_h1("6. RECOMMENDED NEGOTIATION STRATEGY")
    add_body("1. Settle Balance: Request release of the remaining CAD $300 on the original quotation upon delivery of Revision 2 documentation.")
    add_body("2. Focus on Value: Present the technical audit demonstrating the substantial enterprise value already secured by CRBCL.")
    add_body("3. Propose Milestone Addendum: Offer a structured milestone addendum (e.g. $5,000 to $10,000 CAD per operational sprint) to complete live cloud deployment, staff onboarding, and mobile field UAT.")

    doc.save(docx_path)
    print(f"Document 5 Revision 2 DOCX written to: {docx_path}")

    # ─────────────────────────────────────────────────────────
    # 2. BUILD PDF (Target 5-8 pages)
    # ─────────────────────────────────────────────────────────
    pdf_doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = get_pdf_styles_v2()
    story = []

    # Cover Page
    story.append(Spacer(1, 24))
    story.append(Paragraph("CHIEF RED BEAR CHILDREN'S LODGE<br/>ORIGINAL SCOPE VS ADDITIONAL DEVELOPMENT EVIDENCE", styles["CRBCL_CoverTitle"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Factual Evidence Dossier Documenting Commercial Quotation, Scope Additions, and Negotiation Options<br/>Revision 2 — Private Commercial Addendum Prepared for Developer Review", styles["CRBCL_CoverSubtitle"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Client Organization:</b> Chief Red Bear Children's Lodge / Cowessess First Nation, Saskatchewan, Canada<br/>"
        "<b>Technical Baseline:</b> Post-Phase 5 Hardening | <b>Git Commit HEAD:</b> 0746579 | <b>Branch:</b> main<br/>"
        "<b>Repository Path:</b> C:\\Users\\Shilley Pc\\crbcl | <b>Remote:</b> https://github.com/innovatorledger-web/crbcl<br/>"
        "<b>Notice:</b> STRICTLY PRIVATE COMMERCIAL MATERIAL — DO NOT DISTRIBUTE TO CRBCL BOARD OF DIRECTORS",
        styles["CRBCL_CoverMeta"]
    ))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceAfter=12))

    notice_text = (
        "<b>Strict Commercial Confidentiality Notice:</b> This document contains sensitive commercial and contractual information regarding the development of the CRBCL platform. It is strictly segregated from the technical and progress reports provided to the CRBCL Board of Directors. It does NOT assert a legally enforceable debt, nor does it claim that CRBCL leadership has formally approved revised fees. Its sole purpose is to provide an objective, evidence-based factual accounting of the original project agreement versus the massive additive technical scope executed in source code, supporting professional commercial alignment."
    )
    story.append(create_pdf_notice_box_v2("PRIVATE COMMERCIAL DOSSIER NOTICE", notice_text, styles))
    story.append(PageBreak())

    # Section 1: Financial Baseline Table
    story.append(Paragraph("1. FINANCIAL BASELINE & CONTRACTUAL RECORD", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("Below is the verified financial summary of the engagement as of October 2026:", styles["CRBCL_Body"]))

    pdf_fac_rows = [
        [
            Paragraph("<b>Commercial Item</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Recorded Amount</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Factual Basis & Current Legal Status</b>", styles["CRBCL_TableHeader"]),
        ]
    ]
    for fac in COMMERCIAL_FACTS_TABLE:
        pdf_fac_rows.append([
            Paragraph(f"<b>{fac[0]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(f"<b>{fac[1]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(fac[2], styles["CRBCL_TableCell"]),
        ])

    t_fac = Table(pdf_fac_rows, colWidths=[150, 120, 270])
    t_fac.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_fac)
    story.append(Spacer(1, 10))

    # Section 2: Scope Comparison Detailed Table
    story.append(Paragraph("2. GRANULAR COMPARISON: ORIGINAL QUOTATION VS ACTUAL DEVELOPMENT", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("The table below itemizes the 12 core functional domains, comparing what was originally quoted against what was built:", styles["CRBCL_Body"]))

    pdf_cmp_rows = [
        [
            Paragraph("<b>Functional Domain</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Original Quoted Scope ($2,500 CAD)</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Actual Developed Architecture</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Physical Repository Evidence</b>", styles["CRBCL_TableHeader"]),
        ]
    ]
    for cmp_row in SCOPE_COMPARISON_DETAILED:
        pdf_cmp_rows.append([
            Paragraph(f"<b>{cmp_row[0]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(cmp_row[1], styles["CRBCL_TableCell"]),
            Paragraph(cmp_row[2], styles["CRBCL_TableCell"]),
            Paragraph(f"<font size='6.5' color='#64748B'>{cmp_row[3]}</font>", styles["CRBCL_TableCell"]),
        ])

    t_cmp = Table(pdf_cmp_rows, colWidths=[110, 130, 170, 130])
    t_cmp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_cmp)
    story.append(PageBreak())

    # Section 3: Milestone Chronology Table
    story.append(Paragraph("3. CHRONOLOGICAL EVOLUTION OF SCOPE ADDITIONS ACROSS GIT MILESTONES", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("The table below traces the chronological expansion of the platform through verifiable Git commits and database migrations:", styles["CRBCL_Body"]))

    pdf_chr_rows = [
        [
            Paragraph("<b>Evolution Milestone</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Git Commit / Migration</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Scope Expansion Description</b>", styles["CRBCL_TableHeader"]),
        ]
    ]
    for chr_row in MILESTONE_EXPANSION_CHRONOLOGY:
        pdf_chr_rows.append([
            Paragraph(f"<b>{chr_row[0]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(f"<b>{chr_row[1]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(chr_row[2], styles["CRBCL_TableCell"]),
        ])

    t_chr = Table(pdf_chr_rows, colWidths=[140, 130, 270])
    t_chr.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_chr)
    story.append(Spacer(1, 10))

    # Section 4: Analysis of Disequilibrium
    story.append(Paragraph("4. ANALYSIS OF SCOPE EXPANSION & COMMERCIAL DISEQUILIBRIUM", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph(
        "A rigorous technical audit establishes that the delivered software far exceeds the boundaries of the original CAD $2,500 quotation:",
        styles["CRBCL_Body"]
    ))
    story.append(Paragraph("• <b>Scale Divergence:</b> The original quotation contemplated a basic web portal for managing child progress notes. The platform currently contains 205 mapped database entities, 521 REST API endpoints, 327 permission rules, 24 team dashboards, 35 administrative workspaces, and native mobile applications.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Enterprise Capabilities:</b> Specialized First Nations sovereign capabilities—including Case Restriction conflict blinding, Prevention & Healing Excel duplicate quarantine, and custom mobile offline SQLite outbox sync—are enterprise-grade software systems typically valued in high tens of thousands of dollars in commercial software procurement.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Unrepresented Developer Hours:</b> The developer has stated that the original quotation no longer covered the expanded scope, but did not maintain certified timesheets. Consequently, no hourly billing claim is asserted. Instead, the evidence stands on physical source code deliverable scale.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 8))

    # Section 5: Proposed Models
    story.append(Paragraph("5. PROPOSED REVISED COMPENSATION MODELS FOR NEGOTIATION", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("To establish an equitable commercial path forward without creating adversarial disputes, three constructive models are proposed:", styles["CRBCL_Body"]))
    for mod_title, mod_desc in COMPENSATION_MODELS:
        story.append(Paragraph(f"• <b>{mod_title}:</b> {mod_desc}", styles["CRBCL_Body"]))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 8))

    # Section 6: Recommended Strategy
    story.append(Paragraph("6. RECOMMENDED NEGOTIATION STRATEGY", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("1. <b>Settle Balance:</b> Request release of the remaining CAD $300 on the original quotation upon delivery of Revision 2 documentation.", styles["CRBCL_Body"]))
    story.append(Paragraph("2. <b>Focus on Value:</b> Present the technical audit demonstrating the substantial enterprise value already secured by CRBCL.", styles["CRBCL_Body"]))
    story.append(Paragraph("3. <b>Propose Milestone Addendum:</b> Offer a structured milestone addendum (e.g. $5,000 to $10,000 CAD per operational sprint) to complete live cloud deployment, staff onboarding, and mobile field UAT.", styles["CRBCL_Body"]))

    pdf_doc.build(story, canvasmaker=NumberedCanvasV2)
    print(f"Document 5 Revision 2 PDF written to: {pdf_path}")
    return docx_path, pdf_path


if __name__ == "__main__":
    build_doc5()
