"""Generate Document 3: Detailed Feature Completion and Remaining Work Register (DOCX & PDF)."""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib import colors

from scripts.deliverables_generator.common import (
    DELIVERABLES_DIR, NumberedCanvas, get_pdf_styles, create_pdf_notice_box,
    PRIMARY_HEX, SECONDARY_HEX, DARK_HEX, LIGHT_BG_HEX, BORDER_HEX,
    COLOR_PRIMARY, COLOR_SECONDARY, COLOR_DARK, COLOR_LIGHT_BG, COLOR_BORDER,
    set_cell_background, set_cell_margins
)

DOC_NAME_BASE = "CRBCL_Feature_Completion_and_Remaining_Work_Register_October_2026"


def build_docx():
    docx_path = os.path.join(DELIVERABLES_DIR, f"{DOC_NAME_BASE}.docx")
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    header = doc.sections[0].header
    hp = header.paragraphs[0]
    hp.text = "CHIEF RED BEAR CHILDREN'S LODGE — FEATURE COMPLETION REGISTER (OCTOBER 2026)"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.style.font.name = "Arial"
    hp.style.font.size = Pt(8.5)
    hp.style.font.color.rgb = RGBColor(100, 116, 139)

    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = "CONFIDENTIAL — FOR CRBCL LEADERSHIP & TECHNICAL AUDITORS"
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fp.style.font.name = "Arial"
    fp.style.font.size = Pt(8.5)
    fp.style.font.color.rgb = RGBColor(100, 116, 139)

    # Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("CRBCL PLATFORM FEATURE COMPLETION\n& REMAINING WORK REGISTER")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(19)
    r_title.font.color.rgb = RGBColor(107, 29, 47)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Exhaustive Module-by-Module Implementation Audit, File Evidence, and Operationalization Register")
    r_sub.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(201, 138, 44)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_meta = doc.add_paragraph()
    r_meta = p_meta.add_run("Cowessess First Nation | Chief Red Bear Children's Lodge\nPreparation Date: October 27, 2026 | Commit HEAD: 0746579 | Branch: main\nAudit Standards: Rigorous Source Code, Automated Test & Live Inspection")
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(9)
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    def add_sec(h1_text):
        p = doc.add_paragraph()
        r = p.add_run(h1_text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(107, 29, 47)
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)

    def add_body(text, bold_prefix=""):
        p = doc.add_paragraph()
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.bold = True
            rb.font.name = "Arial"
            rb.font.size = Pt(9.5)
            rb.font.color.rgb = RGBColor(30, 41, 59)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_after = Pt(4)

    add_sec("1. AUDIT METHODOLOGY & STATUS TAXONOMY")
    add_body(
        "To provide leadership and independent technical evaluators with unvarnished accuracy, every feature in this register is categorized into one of eight standardized, non-promotional status tiers based on physical source code inspection, test pass results, and live environment checks:"
    )
    add_body("LIVE VERIFIED: Confirmed operating on staging or live environment with end-to-end user verification.", "• ")
    add_body("PRODUCTION DEPLOYED — UAT PENDING: Deployed to live/staging hosting; awaiting authenticated supervisor UAT.", "• ")
    add_body("SOURCE IMPLEMENTED — TESTED: Fully written in backend/frontend with passing automated unit/integration tests.", "• ")
    add_body("SOURCE IMPLEMENTED — BUILD VERIFIED: Source code written and compiles cleanly; pending end-to-end integration tests.", "• ")
    add_body("PARTIALLY IMPLEMENTED: Core data models or basic endpoints created, but workflows or UI forms are incomplete.", "• ")
    add_body("STUBBED / NOT LIVE: Mocked or simulated component; awaits external API key, cloud provisioning, or vendor contract.", "• ")
    add_body("PLANNED / NOT IMPLEMENTED: Documented in future roadmap; no source code or database migrations written yet.", "• ")
    add_body("DECISION PENDING: Awaits formal policy, budget, or architectural approval by the CRBCL Board.", "• ")

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_sec("2. COMPLETE PLATFORM FEATURE AUDIT REGISTER")

    register_table = doc.add_table(rows=21, cols=5)
    register_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Domain / Capability", "Current Status", "Implementation Evidence", "Remaining Requirements", "Blockers / Dependencies"]
    for i, h in enumerate(headers):
        cell = register_table.cell(0, i)
        set_cell_background(cell, PRIMARY_HEX)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8)
        r.font.color.rgb = RGBColor(255, 255, 255)

    entries = [
        ("1. Core Auth & RBAC", "LIVE VERIFIED (Core Auth)", "auth/router.py, users.py, Login.jsx", "Multi-factor SMS authentication setup", "Twilio contract"),
        ("2. Master Person & Client Index", "SOURCE IMPLEMENTED — TESTED", "person.py, client.py, test_client.py", "Finalize legal merge approval workflow", "CRBCL privacy review"),
        ("3. Case Management & Safety Plans", "PRODUCTION DEPLOYED — UAT PENDING", "cases.py, safety_plans.py, TeamDashboard.jsx", "Supervisor sign-off signature capture", "UAT scheduling"),
        ("4. Case Notes & Attachments", "LIVE VERIFIED (Staging UAT)", "case_notes.py, test_case_notes.py", "S3 document storage sync integration", "AWS Canada S3 bucket"),
        ("5. Assessment Engine", "SOURCE IMPLEMENTED — TESTED", "assessments.py, test_assessments.py", "Custom Cowessess assessment forms", "CRBCL policy templates"),
        ("6. Prevention & Healing Workspace", "LIVE VERIFIED (Staging UAT)", "prevention_healing.py, PreventionHealingWorkspace.jsx", "Final supervisor acceptance sign-off", "UAT sign-off"),
        ("7. 3-Tier Duplicate Engine", "LIVE VERIFIED (Staging UAT)", "prevention_healing.py (0746579)", "Fine-tune fuzzy thresholds with real data", "None (Ready)"),
        ("8. Staff Login Quarantine", "LIVE VERIFIED (Protected)", "seed_staging_synthetic.py, auth/service.py", "Admin UI bulk credential activation", "Admin review"),
        ("9. Foster Care & Kinship", "SOURCE IMPLEMENTED — TESTED", "placements.py, CaregiverPortal.jsx", "Police record check upload integration", "Live UAT"),
        ("10. Customary Care Agreements", "SOURCE IMPLEMENTED — TESTED", "customary_care.py, CustomaryCareView.jsx", "Elder council signature protocol", "Elder committee guidance"),
        ("11. Cultural & Healing Tracking", "SOURCE IMPLEMENTED — TESTED", "cultural_healing.py, CulturalDashboard.jsx", "Elder honorarium voucher reconciliation", "Finance alignment"),
        ("12. Youth Transition Support", "SOURCE IMPLEMENTED — TESTED", "youth_services.py, YouthServicesView.jsx", "Independent living stipend calculation", "Policy approval"),
        ("13. Family Support & Vouchers", "PRODUCTION DEPLOYED — UAT PENDING", "family_support.py, FamilySupportView.jsx", "Grocery gift card barcode scanning", "Barcode hardware"),
        ("14. Jordan's Principle Claims", "SOURCE IMPLEMENTED — TESTED", "jordans_principle.py, JordansPrincipleView.jsx", "Federal billing EDI export format", "Indigenous Services Canada format"),
        ("15. Legal & Court Dockets", "SOURCE IMPLEMENTED — TESTED", "legal_court.py, LegalDashboard.jsx", "Court document redaction stamps", "Court liaison feedback"),
        ("16. Front Desk Reception", "PRODUCTION DEPLOYED — UAT PENDING", "front_desk.py, FrontDeskView.jsx", "Visitor badge printer integration", "Hardware setup"),
        ("17. Executive & Board Governance", "LIVE VERIFIED (Staging UAT)", "board_action.py, ExecutiveDashboard.jsx", "Annual aggregate report export (PDF)", "Board approval"),
        ("18. Finance & General Ledger", "SOURCE IMPLEMENTED — TESTED", "finance.py, FinanceDashboard.jsx", "Sage/QuickBooks accounting sync", "Finance software choice"),
        ("19. Fleet & GPS Telematics", "SOURCE IMPLEMENTED — TESTED", "fleet.py, FleetDashboard.jsx", "Live OBD-II GPS telematics webhook", "Geotab/Samsara API key"),
        ("20. Ask Red Bear AI (LLM)", "STUBBED / NOT LIVE", "gateway.py, fake_provider.py, AskRedBear.jsx", "Production Claude 3.5 Sonnet API key", "Board budget approval"),
    ]

    for row_idx, e in enumerate(entries, start=1):
        bg = LIGHT_BG_HEX if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(e):
            cell = register_table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=45, bottom=45, left=60, right=60)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(7.5)
            if col_idx == 0:
                r.bold = True
            if col_idx == 1 and "LIVE VERIFIED" in text:
                r.font.color.rgb = RGBColor(22, 101, 52)  # green
            elif col_idx == 1 and "STUBBED" in text:
                r.font.color.rgb = RGBColor(180, 83, 9)   # amber

    doc.add_paragraph().paragraph_format.space_after = Pt(16)
    doc.save(docx_path)
    print(f"Document 3 DOCX successfully written to: {docx_path}")
    return docx_path


def build_pdf():
    pdf_path = os.path.join(DELIVERABLES_DIR, f"{DOC_NAME_BASE}.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=40,
        rightMargin=40,
        topMargin=45,
        bottomMargin=45,
    )
    styles = get_pdf_styles()
    story = []

    story.append(Paragraph("CRBCL PLATFORM FEATURE COMPLETION<br/>& REMAINING WORK REGISTER", styles["CRBCL_DocTitle"]))
    story.append(Paragraph("Exhaustive Module-by-Module Implementation Audit, File Evidence, and Operationalization Register", styles["CRBCL_DocSubtitle"]))
    story.append(Paragraph("Cowessess First Nation | Chief Red Bear Children's Lodge<br/>Preparation Date: October 27, 2026 | Commit HEAD: 0746579 | Branch: main<br/>Audit Standards: Rigorous Source Code, Automated Test & Live Inspection", styles["CRBCL_MetaText"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=10))

    story.append(Paragraph("1. AUDIT METHODOLOGY & STATUS TAXONOMY", styles["CRBCL_H1"]))
    story.append(Paragraph(
        "To provide leadership and independent technical evaluators with unvarnished accuracy, every feature in this register is categorized into one of eight standardized, non-promotional status tiers: <b>LIVE VERIFIED</b> (Operating on live/staging with UAT sign-off); <b>PRODUCTION DEPLOYED — UAT PENDING</b> (Live on server, awaiting supervisor testing); <b>SOURCE IMPLEMENTED — TESTED</b> (Code written and passed automated test suites); <b>SOURCE IMPLEMENTED — BUILD VERIFIED</b> (Code written and compiles); <b>PARTIALLY IMPLEMENTED</b> (Under development); <b>STUBBED / NOT LIVE</b> (Simulated; awaits live API keys/contracts); <b>PLANNED / NOT IMPLEMENTED</b> (Future roadmap); <b>DECISION PENDING</b> (Awaiting Board governance).",
        styles["CRBCL_Body"]
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. COMPLETE PLATFORM FEATURE AUDIT REGISTER", styles["CRBCL_H1"]))

    reg_rows = [
        [
            Paragraph("<b>Domain / Capability</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Current Status</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Implementation Evidence</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Remaining Requirements</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Blockers / Dependencies</b>", styles["CRBCL_TableHeader"]),
        ],
        [Paragraph("<b>1. Core Auth & RBAC</b>", styles["CRBCL_TableCellBold"]), Paragraph("<font color='#166534'><b>LIVE VERIFIED (Core Auth)</b></font>", styles["CRBCL_TableCell"]), Paragraph("auth/router.py, Login.jsx", styles["CRBCL_TableCell"]), Paragraph("Multi-factor SMS auth", styles["CRBCL_TableCell"]), Paragraph("Twilio contract", styles["CRBCL_TableCell"])],
        [Paragraph("<b>2. Person & Client Index</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("person.py, client.py", styles["CRBCL_TableCell"]), Paragraph("Legal merge approval workflow", styles["CRBCL_TableCell"]), Paragraph("CRBCL privacy review", styles["CRBCL_TableCell"])],
        [Paragraph("<b>3. Case & Safety Plans</b>", styles["CRBCL_TableCellBold"]), Paragraph("PRODUCTION DEPLOYED — UAT PENDING", styles["CRBCL_TableCell"]), Paragraph("cases.py, safety_plans.py", styles["CRBCL_TableCell"]), Paragraph("Supervisor digital signatures", styles["CRBCL_TableCell"]), Paragraph("UAT scheduling", styles["CRBCL_TableCell"])],
        [Paragraph("<b>4. Notes & Attachments</b>", styles["CRBCL_TableCellBold"]), Paragraph("<font color='#166534'><b>LIVE VERIFIED (Staging UAT)</b></font>", styles["CRBCL_TableCell"]), Paragraph("case_notes.py", styles["CRBCL_TableCell"]), Paragraph("S3 cloud storage sync", styles["CRBCL_TableCell"]), Paragraph("AWS Canada S3", styles["CRBCL_TableCell"])],
        [Paragraph("<b>5. Assessment Engine</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("assessments.py", styles["CRBCL_TableCell"]), Paragraph("Custom Cowessess form templates", styles["CRBCL_TableCell"]), Paragraph("Policy templates", styles["CRBCL_TableCell"])],
        [Paragraph("<b>6. Prevention & Healing</b>", styles["CRBCL_TableCellBold"]), Paragraph("<font color='#166534'><b>LIVE VERIFIED (Staging UAT)</b></font>", styles["CRBCL_TableCell"]), Paragraph("prevention_healing.py", styles["CRBCL_TableCell"]), Paragraph("Supervisor acceptance sign-off", styles["CRBCL_TableCell"]), Paragraph("UAT sign-off", styles["CRBCL_TableCell"])],
        [Paragraph("<b>7. 3-Tier Duplicate Engine</b>", styles["CRBCL_TableCellBold"]), Paragraph("<font color='#166534'><b>LIVE VERIFIED (Staging UAT)</b></font>", styles["CRBCL_TableCell"]), Paragraph("prevention_healing.py (0746579)", styles["CRBCL_TableCell"]), Paragraph("Fine-tune thresholds with data", styles["CRBCL_TableCell"]), Paragraph("None (Ready)", styles["CRBCL_TableCell"])],
        [Paragraph("<b>8. Staff Login Quarantine</b>", styles["CRBCL_TableCellBold"]), Paragraph("<font color='#166534'><b>LIVE VERIFIED (Protected)</b></font>", styles["CRBCL_TableCell"]), Paragraph("seed_staging_synthetic.py", styles["CRBCL_TableCell"]), Paragraph("Bulk credential activation UI", styles["CRBCL_TableCell"]), Paragraph("Admin review", styles["CRBCL_TableCell"])],
        [Paragraph("<b>9. Foster Care & Kinship</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("placements.py, CaregiverPortal.jsx", styles["CRBCL_TableCell"]), Paragraph("Police record check integration", styles["CRBCL_TableCell"]), Paragraph("Live UAT", styles["CRBCL_TableCell"])],
        [Paragraph("<b>10. Customary Care</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("customary_care.py", styles["CRBCL_TableCell"]), Paragraph("Elder council signature protocol", styles["CRBCL_TableCell"]), Paragraph("Elder committee guidance", styles["CRBCL_TableCell"])],
        [Paragraph("<b>11. Cultural & Healing</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("cultural_healing.py", styles["CRBCL_TableCell"]), Paragraph("Elder honorarium voucher reconciliation", styles["CRBCL_TableCell"]), Paragraph("Finance alignment", styles["CRBCL_TableCell"])],
        [Paragraph("<b>12. Youth Transitions</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("youth_services.py", styles["CRBCL_TableCell"]), Paragraph("Living stipend calculation", styles["CRBCL_TableCell"]), Paragraph("Policy approval", styles["CRBCL_TableCell"])],
        [Paragraph("<b>13. Family Support</b>", styles["CRBCL_TableCellBold"]), Paragraph("PRODUCTION DEPLOYED — UAT PENDING", styles["CRBCL_TableCell"]), Paragraph("family_support.py", styles["CRBCL_TableCell"]), Paragraph("Gift card barcode scanner support", styles["CRBCL_TableCell"]), Paragraph("Barcode hardware", styles["CRBCL_TableCell"])],
        [Paragraph("<b>14. Jordan's Principle</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("jordans_principle.py", styles["CRBCL_TableCell"]), Paragraph("Federal billing EDI export", styles["CRBCL_TableCell"]), Paragraph("ISC format specs", styles["CRBCL_TableCell"])],
        [Paragraph("<b>15. Legal & Court Dockets</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("legal_court.py", styles["CRBCL_TableCell"]), Paragraph("Court redaction stamps", styles["CRBCL_TableCell"]), Paragraph("Court liaison feedback", styles["CRBCL_TableCell"])],
        [Paragraph("<b>16. Front Desk Reception</b>", styles["CRBCL_TableCellBold"]), Paragraph("PRODUCTION DEPLOYED — UAT PENDING", styles["CRBCL_TableCell"]), Paragraph("front_desk.py", styles["CRBCL_TableCell"]), Paragraph("Visitor badge printer support", styles["CRBCL_TableCell"]), Paragraph("Hardware setup", styles["CRBCL_TableCell"])],
        [Paragraph("<b>17. Executive & Governance</b>", styles["CRBCL_TableCellBold"]), Paragraph("<font color='#166534'><b>LIVE VERIFIED (Staging UAT)</b></font>", styles["CRBCL_TableCell"]), Paragraph("board_action.py", styles["CRBCL_TableCell"]), Paragraph("Annual PDF report export", styles["CRBCL_TableCell"]), Paragraph("Board approval", styles["CRBCL_TableCell"])],
        [Paragraph("<b>18. Finance & Ledger</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("finance.py", styles["CRBCL_TableCell"]), Paragraph("Sage/QuickBooks accounting sync", styles["CRBCL_TableCell"]), Paragraph("Finance software choice", styles["CRBCL_TableCell"])],
        [Paragraph("<b>19. Fleet & Telematics</b>", styles["CRBCL_TableCellBold"]), Paragraph("SOURCE IMPLEMENTED — TESTED", styles["CRBCL_TableCell"]), Paragraph("fleet.py", styles["CRBCL_TableCell"]), Paragraph("Live OBD-II GPS webhook", styles["CRBCL_TableCell"]), Paragraph("Geotab/Samsara API key", styles["CRBCL_TableCell"])],
        [Paragraph("<b>20. Ask Red Bear AI</b>", styles["CRBCL_TableCellBold"]), Paragraph("<font color='#b45309'><b>STUBBED / NOT LIVE</b></font>", styles["CRBCL_TableCell"]), Paragraph("gateway.py, fake_provider.py", styles["CRBCL_TableCell"]), Paragraph("Production Claude 3.5 Sonnet API key", styles["CRBCL_TableCell"]), Paragraph("Board budget approval", styles["CRBCL_TableCell"])],
    ]

    t_reg = Table(reg_rows, colWidths=[105, 115, 110, 110, 92])
    t_reg.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_reg)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Document 3 PDF successfully written to: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    build_docx()
    build_pdf()
