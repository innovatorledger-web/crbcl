"""Generate Document 4: Ask Red Bear Development and Completion Assessment (DOCX & PDF)."""

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

DOC_NAME_BASE = "CRBCL_Ask_Red_Bear_Development_Status_and_Completion_Assessment_October_2026"


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
    hp.text = "CHIEF RED BEAR CHILDREN'S LODGE — ASK RED BEAR AI ASSESSMENT (OCTOBER 2026)"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.style.font.name = "Arial"
    hp.style.font.size = Pt(8.5)
    hp.style.font.color.rgb = RGBColor(100, 116, 139)

    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = "CONFIDENTIAL — STRICTLY FOR CRBCL LEADERSHIP & AI GOVERNANCE"
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fp.style.font.name = "Arial"
    fp.style.font.size = Pt(8.5)
    fp.style.font.color.rgb = RGBColor(100, 116, 139)

    # Title
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("ASK RED BEAR ASSISTIVE AI\nDEVELOPMENT STATUS & COMPLETION ASSESSMENT")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(19)
    r_title.font.color.rgb = RGBColor(107, 29, 47)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Comprehensive Technical Audit of Assistive AI Architecture, Speech Pipeline, Sovereign Governance, and Production Roadmap")
    r_sub.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(11)
    r_sub.font.color.rgb = RGBColor(201, 138, 44)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_meta = doc.add_paragraph()
    r_meta = p_meta.add_run("Cowessess First Nation | Chief Red Bear Children's Lodge\nPreparation Date: October 27, 2026 | Commit HEAD: 0746579 | Branch: main\nGovernance Classification: Strictly Assistive AI — Human-in-the-Loop Guaranteed")
    r_meta.font.name = "Arial"
    r_meta.font.size = Pt(9)
    r_meta.font.color.rgb = RGBColor(100, 116, 139)
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Mandatory Notice Box
    notice_table = doc.add_table(rows=1, cols=1)
    notice_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = notice_table.cell(0, 0)
    set_cell_background(cell, "FEF3C7")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
    np = cell.paragraphs[0]
    nr_head = np.add_run("⚠️ MANDATORY AI ASSISTIVE & LEGAL NOTICE\n\n")
    nr_head.bold = True
    nr_head.font.size = Pt(10)
    nr_head.font.color.rgb = RGBColor(146, 64, 14)

    nr_body = np.add_run(
        "Ask Red Bear is strictly assistive and advisory. It possesses zero legal authority to make autonomous child welfare screenings, custody determinations, or statutory child protection decisions. All outputs are generated as assistive drafts and require independent human review and legal verification by a qualified CRBCL caseworker or supervisor. Crucially, the backend completion engine currently runs on a simulated provider (FakeAiProvider); live cloud LLM integration requires CRBCL Board budget authorization and provider selection."
    )
    nr_body.font.size = Pt(9)
    nr_body.font.color.rgb = RGBColor(120, 53, 15)

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    def add_sec(h1_text):
        p = doc.add_paragraph()
        r = p.add_run(h1_text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(13)
        r.font.color.rgb = RGBColor(107, 29, 47)
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(5)

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
        p.paragraph_format.space_after = Pt(5)

    add_sec("1. EXECUTIVE SUMMARY & ASSISTIVE SCOPE")
    add_body(
        "Ask Red Bear is a custom-engineered artificial intelligence capability embedded within the CRBCL Family Wellness platform. Developed to alleviate heavy administrative burdens on frontline caseworkers, Ask Red Bear provides natural language record retrieval, schedule summarization, and hands-free voice transcription. In strict compliance with Indigenous OCAP® data principles and Canadian child welfare standards, the system is designed never to make autonomous decisions or replace human caseworkers."
    )

    add_sec("2. CURRENT ARCHITECTURAL STATE & SIMULATION DISCLOSURE")
    add_body(
        "To ensure total transparency with CRBCL leadership, the current implementation status of Ask Red Bear components is detailed below:"
    )
    add_body("LIVE VERIFIED (Backend RBAC & Logic): The Authorization-First Context Gateway, active Case Restriction filters, deterministic tool routing (get_case_summary, get_my_cases, get_overdue_goals), field-level redactions, and database audit logging are 100% written, integrated, and verified with passing automated test suites (test_ask_red_bear_speech.py).", "• ")
    add_body("STUBBED / SIMULATED (LLM Generation): The final model completion step in gateway.py currently utilizes FakeAiProvider (generating synthetic assistive summaries). No live API keys for external cloud LLMs (such as Anthropic Claude 3.5 Sonnet or OpenAI GPT-4o) have been stored in the production environment. This intentional design prevents unmonitored API billing until leadership authorizes an enterprise AI budget.", "• ")
    add_body("LIVE VERIFIED (Speech-to-Text Input Aid): The browser-based speech dictation interface (SpeechDictationControl.jsx) and backend transcription endpoint (/api/v1/ask-red-bear/transcribe) function as an ephemeral input aid. In-memory audio recordings are transcribed directly into the text box for user review and editing before prompt dispatch.", "• ")

    add_sec("3. AUTHORIZATION-FIRST SECURITY & FIELD REDACTION ENGINE")
    add_body(
        "Ask Red Bear implements rigorous defense-in-depth protections to prevent unauthorized data exposure, hallucination, or prompt injection:"
    )

    sec_table = doc.add_table(rows=5, cols=3)
    sec_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["Security Control Layer", "Implementation Mechanism", "Child Welfare Protection Benefit"]
    for i, h in enumerate(s_headers):
        cell = sec_table.cell(0, i)
        set_cell_background(cell, PRIMARY_HEX)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    s_data = [
        ("Prompt Guard Filter", "inspect_prompt_safety() regex & semantic check", "Rejects prompt injection, jailbreak attempts, or instructions to ignore system safety rules."),
        ("Case Restriction Enforcement", "AiGateway.get_authorized_case_ids()", "Completely excludes cases from retrieval context if the user has a registered family conflict of interest."),
        ("Field-Level Redaction", "Dynamic JSON stripping before prompt compilation", "Automatically removes child medical notes, reporter identities, and financial accounts unless explicitly permitted."),
        ("Immutable AI Audit Ledger", "AiRequestAudit database table logging", "Logs user ID, prompt token counts, latency, and estimated cost in CAD for every single AI interaction."),
    ]

    for row_idx, sd in enumerate(s_data, start=1):
        bg = LIGHT_BG_HEX if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(sd):
            cell = sec_table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(8)
            if col_idx == 0:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_sec("4. KNOWLEDGE BASE & RETRIEVAL-AUGMENTED GENERATION (RAG) REQUIREMENTS")
    add_body(
        "To elevate Ask Red Bear from simple database querying to a comprehensive knowledge assistant, a sovereign Retrieval-Augmented Generation (RAG) pipeline is recommended. Key requirements include:"
    )
    add_body("1. Cowessess First Nation Miyo-Pimatisiwin Act Ingestion: Chunking, indexing, and embedding the full statutory text of the Cowessess Child and Family Wellness legislation so Ask Red Bear can cite specific legal sections when answering caseworker questions.", "• ")
    add_body("2. CRBCL Operational Policy Ingestion: Vectorizing internal manuals regarding customary care protocols, travel mileage reimbursements, and emergency after-hours intake procedures.", "• ")
    add_body("3. Sovereign Vector Storage: Enabling pgvector within the existing PostgreSQL database to ensure all vector embeddings and search indexes remain within CRBCL's sovereign boundary, avoiding external vector databases.", "• ")

    add_sec("5. PRODUCTION PROVIDER COMPARISON & COST PROJECTIONS")
    add_body(
        "CRBCL leadership has three viable architectural pathways for powering live completion in Ask Red Bear:"
    )

    prov_table = doc.add_table(rows=4, cols=4)
    prov_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    p_headers = ["Provider Option", "Data Sovereignty & Privacy", "Estimated Monthly Cost", "Recommendation"]
    for i, h in enumerate(p_headers):
        cell = prov_table.cell(0, i)
        set_cell_background(cell, PRIMARY_HEX)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    p_data = [
        ("Option A: Anthropic Claude 3.5 Sonnet (AWS Canada)", "Data remains within Canada (ca-central-1); zero model training on customer data.", "$150–$300 CAD / mo (approx. 10,000 queries)", "RECOMMENDED: Highest reasoning, strong safety guardrails, low cost."),
        ("Option B: Microsoft Azure OpenAI (Canada East)", "HIPAA/SOC2 certified; isolated Canadian enterprise tenant.", "$200–$400 CAD / mo", "VIABLE ALTERNATIVE: Seamless if CRBCL adopts Microsoft 365."),
        ("Option C: Self-Hosted Sovereign Model (Llama-3 on GPU)", "100% on-premise Cowessess data sovereignty; zero third-party transmission.", "$600–$1,200 CAD / mo (dedicated GPU hardware)", "HIGH SECURITY OPTION: Ideal long-term for complete sovereign isolation."),
    ]

    for row_idx, pd in enumerate(p_data, start=1):
        bg = LIGHT_BG_HEX if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(pd):
            cell = prov_table.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
            p = cell.paragraphs[0]
            r = p.add_run(text)
            r.font.size = Pt(7.5)
            if col_idx == 0:
                r.bold = True

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    add_sec("6. OPERATIONAL COMPLETION ROADMAP")
    add_body(
        "Finalizing Ask Red Bear for frontline caseworkers requires a straightforward 6-week execution plan:"
    )
    add_body("Weeks 1–2: Board approval of AI budget and signing of enterprise sovereign agreement with Anthropic AWS Canada.", "• ")
    add_body("Weeks 3–4: Ingest Cowessess Miyo-Pimatisiwin Act into pgvector database; conduct prompt testing with senior caseworkers.", "• ")
    add_body("Weeks 5–6: Deploy live API keys, establish automated monthly token cost alerts, and conduct mandatory caseworker AI ethics training.", "• ")

    doc.add_paragraph().paragraph_format.space_after = Pt(16)
    doc.save(docx_path)
    print(f"Document 4 DOCX successfully written to: {docx_path}")
    return docx_path


def build_pdf():
    pdf_path = os.path.join(DELIVERABLES_DIR, f"{DOC_NAME_BASE}.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    styles = get_pdf_styles()
    story = []

    story.append(Paragraph("ASK RED BEAR ASSISTIVE AI<br/>DEVELOPMENT STATUS & COMPLETION ASSESSMENT", styles["CRBCL_DocTitle"]))
    story.append(Paragraph("Comprehensive Technical Audit of Assistive AI Architecture, Speech Pipeline, Sovereign Governance, and Production Roadmap", styles["CRBCL_DocSubtitle"]))
    story.append(Paragraph("Cowessess First Nation | Chief Red Bear Children's Lodge<br/>Preparation Date: October 27, 2026 | Commit HEAD: 0746579 | Branch: main<br/>Governance Classification: Strictly Assistive AI — Human-in-the-Loop Guaranteed", styles["CRBCL_MetaText"]))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY, spaceAfter=14))

    notice_text = (
        "<b>Ask Red Bear is strictly assistive and advisory.</b> It possesses zero legal authority to make autonomous child welfare screenings, custody determinations, or statutory child protection decisions. All outputs are generated as assistive drafts and require independent human review and legal verification by a qualified CRBCL caseworker or supervisor. Crucially, the backend completion engine currently runs on a simulated provider (FakeAiProvider); live cloud LLM integration requires CRBCL Board budget authorization and provider selection."
    )
    story.append(create_pdf_notice_box("MANDATORY AI ASSISTIVE & LEGAL NOTICE", notice_text, styles))
    story.append(Spacer(1, 14))

    story.append(Paragraph("1. EXECUTIVE SUMMARY & ASSISTIVE SCOPE", styles["CRBCL_H1"]))
    story.append(Paragraph(
        "Ask Red Bear is a custom-engineered artificial intelligence capability embedded within the CRBCL Family Wellness platform. Developed to alleviate heavy administrative burdens on frontline caseworkers, Ask Red Bear provides natural language record retrieval, schedule summarization, and hands-free voice transcription. In strict compliance with Indigenous OCAP® data principles and Canadian child welfare standards, the system is designed never to make autonomous decisions or replace human caseworkers.",
        styles["CRBCL_Body"]
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("2. CURRENT ARCHITECTURAL STATE & SIMULATION DISCLOSURE", styles["CRBCL_H1"]))
    story.append(Paragraph("• <b>LIVE VERIFIED (Backend RBAC & Logic):</b> The Authorization-First Context Gateway, active Case Restriction filters, deterministic tool routing (get_case_summary, get_my_cases, get_overdue_goals), field redactions, and database audit logging are 100% written, integrated, and verified with passing automated test suites (test_ask_red_bear_speech.py).", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>STUBBED / SIMULATED (LLM Generation):</b> The final model completion step in gateway.py currently utilizes FakeAiProvider (generating synthetic assistive summaries). No live API keys for external cloud LLMs (such as Anthropic Claude 3.5 Sonnet or OpenAI GPT-4o) have been stored in the production environment. This intentional design prevents unmonitored API billing until leadership authorizes an enterprise AI budget.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>LIVE VERIFIED (Speech-to-Text Input Aid):</b> The browser-based speech dictation interface (SpeechDictationControl.jsx) and backend transcription endpoint (/api/v1/ask-red-bear/transcribe) function as an ephemeral input aid. In-memory audio recordings are transcribed directly into the text box for user review and editing before prompt dispatch.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("3. AUTHORIZATION-FIRST SECURITY & FIELD REDACTION ENGINE", styles["CRBCL_H1"]))
    story.append(Paragraph(
        "Ask Red Bear implements rigorous defense-in-depth protections to prevent unauthorized data exposure, hallucination, or prompt injection:",
        styles["CRBCL_Body"]
    ))

    sec_rows = [
        [Paragraph("<b>Security Control Layer</b>", styles["CRBCL_TableHeader"]), Paragraph("<b>Implementation Mechanism</b>", styles["CRBCL_TableHeader"]), Paragraph("<b>Child Welfare Protection Benefit</b>", styles["CRBCL_TableHeader"])],
        [Paragraph("<b>Prompt Guard Filter</b>", styles["CRBCL_TableCellBold"]), Paragraph("inspect_prompt_safety() regex & semantic check", styles["CRBCL_TableCell"]), Paragraph("Rejects prompt injection, jailbreak attempts, or instructions to ignore system safety rules.", styles["CRBCL_TableCell"])],
        [Paragraph("<b>Case Restrictions</b>", styles["CRBCL_TableCellBold"]), Paragraph("AiGateway.get_authorized_case_ids()", styles["CRBCL_TableCell"]), Paragraph("Completely excludes cases from retrieval context if the user has a registered family conflict of interest.", styles["CRBCL_TableCell"])],
        [Paragraph("<b>Field Redaction</b>", styles["CRBCL_TableCellBold"]), Paragraph("Dynamic JSON stripping before prompt compilation", styles["CRBCL_TableCell"]), Paragraph("Automatically removes child medical notes, reporter identities, and financial accounts unless explicitly permitted.", styles["CRBCL_TableCell"])],
        [Paragraph("<b>Immutable AI Audit</b>", styles["CRBCL_TableCellBold"]), Paragraph("AiRequestAudit database table logging", styles["CRBCL_TableCell"]), Paragraph("Logs user ID, prompt token counts, latency, and estimated cost in CAD for every single AI interaction.", styles["CRBCL_TableCell"])],
    ]

    t_sec = Table(sec_rows, colWidths=[120, 180, 204])
    t_sec.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sec)
    story.append(Spacer(1, 12))

    story.append(Paragraph("4. KNOWLEDGE BASE & RETRIEVAL-AUGMENTED GENERATION (RAG)", styles["CRBCL_H1"]))
    story.append(Paragraph("• <b>Cowessess Miyo-Pimatisiwin Act Ingestion:</b> Chunking, indexing, and embedding the full statutory text of the Cowessess Child and Family Wellness legislation so Ask Red Bear can cite specific legal sections.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>CRBCL Operational Policy Ingestion:</b> Vectorizing internal manuals regarding customary care protocols, travel mileage reimbursements, and emergency after-hours intake procedures.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Sovereign Vector Storage:</b> Enabling pgvector within the existing PostgreSQL database to ensure all vector embeddings remain strictly within CRBCL's sovereign boundary.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. PRODUCTION PROVIDER COMPARISON & COST PROJECTIONS", styles["CRBCL_H1"]))

    prov_rows = [
        [Paragraph("<b>Provider Option</b>", styles["CRBCL_TableHeader"]), Paragraph("<b>Data Sovereignty & Privacy</b>", styles["CRBCL_TableHeader"]), Paragraph("<b>Estimated Monthly Cost</b>", styles["CRBCL_TableHeader"]), Paragraph("<b>Recommendation</b>", styles["CRBCL_TableHeader"])],
        [Paragraph("<b>Option A: Anthropic Claude 3.5 Sonnet (AWS Canada)</b>", styles["CRBCL_TableCellBold"]), Paragraph("Data remains within Canada (ca-central-1); zero model training on customer data.", styles["CRBCL_TableCell"]), Paragraph("$150–$300 CAD / mo (~10,000 queries)", styles["CRBCL_TableCell"]), Paragraph("<b>RECOMMENDED:</b> Highest reasoning, strong safety guardrails, low cost.", styles["CRBCL_TableCell"])],
        [Paragraph("<b>Option B: Azure OpenAI (Canada East)</b>", styles["CRBCL_TableCellBold"]), Paragraph("HIPAA/SOC2 certified; isolated Canadian enterprise tenant.", styles["CRBCL_TableCell"]), Paragraph("$200–$400 CAD / mo", styles["CRBCL_TableCell"]), Paragraph("<b>VIABLE ALTERNATIVE:</b> Seamless if CRBCL adopts Microsoft 365.", styles["CRBCL_TableCell"])],
        [Paragraph("<b>Option C: Self-Hosted Llama-3 (On-Premise)</b>", styles["CRBCL_TableCellBold"]), Paragraph("100% on-premise Cowessess data sovereignty; zero third-party transmission.", styles["CRBCL_TableCell"]), Paragraph("$600–$1,200 CAD / mo (dedicated GPU)", styles["CRBCL_TableCell"]), Paragraph("<b>HIGH SECURITY OPTION:</b> Ideal long-term for complete sovereign isolation.", styles["CRBCL_TableCell"])],
    ]

    t_prov = Table(prov_rows, colWidths=[110, 140, 110, 144])
    t_prov.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_prov)
    story.append(Spacer(1, 12))

    story.append(Paragraph("6. OPERATIONAL COMPLETION ROADMAP", styles["CRBCL_H1"]))
    story.append(Paragraph("• <b>Weeks 1–2:</b> Board approval of AI budget and signing of enterprise sovereign agreement with Anthropic AWS Canada.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Weeks 3–4:</b> Ingest Cowessess Miyo-Pimatisiwin Act into pgvector database; conduct prompt testing with senior caseworkers.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Weeks 5–6:</b> Deploy live API keys, establish automated monthly token cost alerts, and conduct mandatory caseworker AI ethics training.", styles["CRBCL_Body"]))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Document 4 PDF successfully written to: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    build_docx()
    build_pdf()
