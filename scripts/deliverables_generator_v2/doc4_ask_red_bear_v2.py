"""Generate Document 4 Revision 2: Ask Red Bear Development Status and Completion Assessment (DOCX & PDF).
Target page range: 6-10 substantive pages.
Features an exhaustive, evidence-based assessment of the Ask Red Bear assistant,
rigorously distinguishing live-verified speech transcription from stubbed AI answer generation.
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

DOC_NAME_BASE = "CRBCL_Ask_Red_Bear_Development_Status_and_Completion_Assessment_Revision_2_October_2026"

ASK_RED_BEAR_ARCHITECTURE_DIAGRAM = """
+----------------------------------------------------------------------------------------------------+
|                         ASK RED BEAR DUAL-SUBSYSTEM ARCHITECTURE                                   |
+----------------------------------------------------------------------------------------------------+
|                                                                                                    |
|  [ FRONTEND PRESENTATION LAYER (React 18 / Tailwind CSS) ]                                        |
|  +--------------------------------------------------------------------------------+                |
|  |  AskRedBearModal.jsx / Floating Chat Widget:                                   |                |
|  |  * Text Input Area (Caseworker types or edits transcribed text)                |                |
|  |  * Microphone Dictation Button (Web Audio API / MediaRecorder)                 |                |
|  |  * Dual Mode: Casework Voice Dictation Aid vs AI Policy Consultation           |                |
|  +-----------------------+--------------------------------+-----------------------+                |
|                          |                                |                                        |
|  Microphone Audio Stream | (Base64 WebM/WAV)              | Text Inquiry Submission                |
|                          v                                v (JSON Payload)                         |
|  +-----------------------------------+        +-----------------------------------+                |
|  | SUBSYSTEM A: SPEECH TRANSCRIPTION |        | SUBSYSTEM B: AI ANSWER GENERATION |                |
|  | [ STATUS: LIVE VERIFIED ]         |        | [ STATUS: STUBBED / NOT LIVE ]    |                |
|  +-----------------------------------+        +-----------------------------------+                |
|  | Endpoint:                         |        | Endpoint:                         |                |
|  | POST /api/v1/ask-red-bear/        |        | POST /api/v1/ask-red-bear/query   |                |
|  |        transcribe                 |        |                                   |                |
|  |                                   |        |                                   |                |
|  | Implementation:                   |        | Implementation:                   |                |
|  | * Ephemeral Audio Buffer          |        | * backend/app/services/           |                |
|  | * Streaming Whisper Gateway       |        |   ai_gateway.py                   |                |
|  | * Returns Transcribed String      |        | * Active Provider: FakeAiProvider |                |
|  | * No Audio / Text Persisted       |        | * Returns Hardcoded Simulation    |                |
|  | * Operational on Production Site  |        | * NO Live Cloud LLM Connected     |                |
|  +-----------------+-----------------+        +-----------------+-----------------+                |
|                    |                                            |                                  |
|                    v Transcribed Text Returned                  v Pending Implementation:          |
|  +-----------------------------------+        +-----------------------------------+                |
|  | Textarea in Browser UI:           |        | Required Sovereign Architecture:  |                |
|  | Caseworker reviews, corrects, and |        | * pgvector RAG Knowledge Store    |                |
|  | approves text before inserting    |        | * Cowessess Act & Policy Embeddings|                |
|  | into Case Note or submitting      |        | * RBAC Access & Conflict Blinding |                |
|  | inquiry to backend.               |        | * Cloud LLM API (Pending Board Sel)|                |
|  +-----------------------------------+        +-----------------------------------+                |
|                                                                                                    |
+----------------------------------------------------------------------------------------------------+
"""

CAPABILITY_AUDIT_DATA = [
    ("Frontend Chat Widget & Modal", "AskRedBearModal.jsx, FloatingRedBear.jsx", "LIVE VERIFIED", "Responsive overlay modal, expandable drawer, conversation history UI, and input state transitions."),
    ("Microphone Web Audio Capture", "SpeechRecorder.jsx, audio_utils.js", "LIVE VERIFIED", "Browser MediaStream capture, 16kHz audio downsampling, WebM/WAV encoding, visual VU meter waveform."),
    ("Speech-to-Text Transcription", "POST /api/v1/ask-red-bear/transcribe", "LIVE VERIFIED", "FastAPI transcription bridge; ephemeral audio processing; tested operational on https://genserver.online."),
    ("Transcribed Text In-Place Editing", "Textarea event binding in React", "LIVE VERIFIED", "Spoken words stream into editable textarea; caseworker can manually correct names and Cree terminology."),
    ("Audio Privacy & Ephemeral Buffering", "In-memory BytesIO streaming", "LIVE VERIFIED", "Zero audio disk persistence; audio stream discarded immediately following text transcription extraction."),
    ("AI Gateway Abstraction Interface", "backend/app/services/ai_gateway.py", "SOURCE IMPLEMENTED", "Clean provider interface pattern (AiProvider base class) supporting interchangeable LLM backends."),
    ("FakeAiProvider Simulation Engine", "app/services/ai_gateway.py:FakeAiProvider", "STUBBED / NOT LIVE", "Deterministic mock response generator; returns simulated answers for local integration testing."),
    ("Live Cloud LLM Inference Engine", "Candidate Cloud LLMs (Claude, Azure OpenAI, Sovereign Model)", "PLANNED / NOT IMPLEMENTED", "Direct integration with commercial or sovereign cloud LLM API; pending Board evaluation, selection, and API key procurement."),
    ("RAG Vector Document Indexing", "PostgreSQL pgvector extension", "PLANNED / NOT IMPLEMENTED", "Vectorized knowledge store of Cowessess Miyo-Pimatisiwin Act, CRBCL practice manuals, and policies."),
    ("Role-Aware Context Blinding", "RAG security filter middleware", "PLANNED / NOT IMPLEMENTED", "Enforcement of RBAC permissions and Case Restrictions to ensure AI never leaks confidential family data."),
    ("Prompt Injection & Guardrails", "Input sanitization & boundary prompts", "PLANNED / NOT IMPLEMENTED", "System prompt hardening preventing adversarial extraction of system instructions or protected records."),
    ("First Nations OCAP® Data Sovereignty", "Canadian sovereign data hosting boundary", "DECISION PENDING", "Contractual and technical guarantees that CRBCL queries and embeddings are never used for model training."),
]

PROPOSED_RAG_PIPELINE = [
    ("1. Approved Knowledge Ingestion", "CRBCL policy directors provide authoritative PDF/DOCX documents: Cowessess Child & Family Services Act, Miyo-Pimatisiwin Act regulations, practice guidelines, supervisor manuals, and standard operating procedures. Documents are cryptographically hashed and versioned."),
    ("2. Document Chunking & Vectorization", "Text is segmented into 500-token semantic chunks with 100-token overlap. Each chunk is passed to a text-embedding model (e.g. text-embedding-3-small or self-hosted BGE-large) generating 1536-dimensional dense vectors."),
    ("3. Sovereign Relational Storage", "Embeddings are stored in CRBCL's managed PostgreSQL database using the pgvector extension. Each chunk is tagged with metadata: document_id, section_name, effective_date, required_role, and classification_level."),
    ("4. Semantic Retrieval & RBAC Filtering", "When a user submits a question, their query is vectorized. An approximate nearest neighbor (ANN) cosine similarity search retrieves the top-k most relevant policy chunks. A strict RBAC filter purges any chunks exceeding the user's role authorization."),
    ("5. Context Construction & System Prompting", "The retrieved chunks are injected into a hardened system prompt: 'You are Ask Red Bear, an internal knowledge assistant for Chief Red Bear Children's Lodge. Answer the caseworker's question strictly using the provided Cowessess First Nation policy context below. If the context does not contain the answer, state that you do not know and advise consulting a supervisor. Never invent policies.'"),
    ("6. Cloud Inference & Audit Logging", "The prompt is dispatched via TLS 1.3 to an approved cloud LLM provider (configured with zero-data-retention terms). The generated response is returned to the user, and an immutable record (user_id, timestamp, token_count, retrieved_chunk_ids) is logged for quality audits."),
]

COMPARISON_MATRIX = [
    ("Core Primary Purpose", "Frontline dictation aid to accelerate typing case notes and intake summaries.", "Intelligent policy advisory assistant answering practice and governance questions."),
    ("Current Physical Status", "LIVE VERIFIED on live website (https://genserver.online).", "STUBBED / NOT LIVE in backend (routes to FakeAiProvider)."),
    ("Data Persistence Standard", "Zero persistence; ephemeral in-memory audio buffer discarded immediately.", "Proposed immutable audit log of policy inquiries and retrieved citations."),
    ("External Cloud Dependency", "Whisper STT service (local container or fast API bridge).", "Requires sovereign enterprise API key for Board-approved cloud LLM provider."),
    ("First Nations Privacy Risk", "Very low; audio is never stored; text is explicitly reviewed by caseworker.", "Moderate to high; requires strict prompt boundaries and zero-data-retention agreements."),
    ("Caseworker Autonomy", "High; caseworker maintains 100% editorial control over typed words.", "Advisory only; answers must cite specific Cowessess Act sections."),
    ("Readiness for Daily Work", "100% operationally ready and currently accessible to staff.", "Requires 4-6 weeks of knowledge curation, vector indexing, and supervisor testing."),
]


def build_doc4():
    docx_path = os.path.join(DELIVERABLES_V2_DIR, f"{DOC_NAME_BASE}.docx")
    pdf_path = os.path.join(DELIVERABLES_V2_DIR, f"{DOC_NAME_BASE}.pdf")

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
    hp.text = "CRBCL ASK RED BEAR DEVELOPMENT STATUS & COMPLETION ASSESSMENT (REVISION 2)"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.style.font.name = "Arial"
    hp.style.font.size = Pt(8.5)
    hp.style.font.color.rgb = RGBColor(100, 116, 139)

    footer = doc.sections[0].footer
    fp = footer.paragraphs[0]
    fp.text = "CONFIDENTIAL — STRICTLY FOR TECHNICAL AUDITORS & BOARD REVIEW"
    fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    fp.style.font.name = "Arial"
    fp.style.font.size = Pt(8.5)
    fp.style.font.color.rgb = RGBColor(100, 116, 139)

    # Document Header
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("CHIEF RED BEAR CHILDREN'S LODGE\nASK RED BEAR DEVELOPMENT STATUS & COMPLETION ASSESSMENT")
    r_title.bold = True
    r_title.font.name = "Arial"
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = RGBColor(107, 29, 47)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Evidence-Based Evaluation of Frontline Speech Transcription vs AI Answer Generation\nRevision 2 — Clear Operational Differentiation & Sovereign Completion Roadmap")
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
        "Audience: CRBCL Board of Directors, Executive Leadership, IT Steering Committee, and Independent Evaluators"
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

    def add_code(text):
        p = doc.add_paragraph()
        r = p.add_run(text)
        r.font.name = "Consolas"
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        p.paragraph_format.space_after = Pt(4)
        return p

    add_body("CRITICAL ARCHITECTURAL DISTINCTION NOTICE FOR CRBCL LEADERSHIP:")
    add_body(
        "To eliminate any misunderstanding regarding the development status of 'Ask Red Bear', this assessment explicitly separates two fundamentally distinct technical capabilities: (1) Frontline Speech-to-Text Transcription, which converts spoken voice audio into an editable text string inside the user's browser; and (2) AI Answer Generation, which parses natural language questions, searches an organizational knowledge base, and synthesizes intelligent answers. The former is LIVE VERIFIED on the production website; the latter is STUBBED / NOT LIVE via a simulation provider (FakeAiProvider) and has never been connected to a live cloud large language model (LLM)."
    )

    add_h1("1. EXECUTIVE SUMMARY & DEVELOPMENT REALITY")
    add_body("Previous documentation created the impression that Ask Red Bear was an operational artificial intelligence assistant capable of autonomous child welfare practice consultation. A rigorous source-code audit reveals the precise technical reality:")
    add_body("• Speech-to-Text Dictation is fully implemented and live-verified. When a caseworker clicks the microphone button, audio is recorded, streamed to the backend transcription endpoint, converted into text, and placed into the textarea. No audio recordings or text transcripts are permanently saved to disk, preserving client confidentiality.")
    add_body("• Artificial Intelligence Answer Generation is stubbed in source code. In backend/app/services/ai_gateway.py, the active provider is configured as FakeAiProvider. When a user submits a question, the backend returns simulated pre-canned text. There is no active API connection to OpenAI, Anthropic, or any other cloud LLM on production.")
    add_body("• Operational Impact: Caseworkers currently possess a highly useful voice dictation tool for drafting progress notes and inquiries, but they do NOT possess an intelligent policy advisory assistant. Full implementation requires Board approval of cloud AI terms, knowledge base curation, and RAG vector infrastructure.")

    add_h1("2. DUAL-SUBSYSTEM ARCHITECTURE & DATA FLOW")
    add_body("The diagram below illustrates the exact separation between the live speech transcription subsystem and the stubbed AI generation gateway:")
    add_code(ASK_RED_BEAR_ARCHITECTURE_DIAGRAM.strip())

    add_h1("3. COMPARATIVE ANALYSIS: SPEECH DICTATION VS AI GENERATION")
    add_body("To ensure complete conceptual clarity, the table below compares the two subsystems across all operational, technical, and governance criteria:")
    t_docx_cmp = doc.add_table(rows=1 + len(COMPARISON_MATRIX), cols=3)
    t_docx_cmp.style = "Table Grid"
    hdr_cells_cmp = t_docx_cmp.rows[0].cells
    hdr_titles_cmp = ["Evaluation Dimension", "Speech-to-Text Transcription (Subsystem A)", "AI Answer Generation (Subsystem B)"]
    for idx, name in enumerate(hdr_titles_cmp):
        hdr_cells_cmp[idx].text = name
        set_cell_background(hdr_cells_cmp[idx], PRIMARY_HEX)
        set_cell_margins(hdr_cells_cmp[idx], top=60, bottom=60, left=60, right=60)
        p = hdr_cells_cmp[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, cmp_row in enumerate(COMPARISON_MATRIX):
        row_cells = t_docx_cmp.rows[r_idx + 1].cells
        for c_idx, val in enumerate(cmp_row):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], LIGHT_BG_HEX if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=50, right=50)
            p = row_cells[c_idx].paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(7.5)
            if c_idx == 0:
                r.bold = True

    add_h1("4. DETAILED AUDIT OF 12 ASK RED BEAR CAPABILITIES")
    add_body("Below is an audited inventory of all 12 frontend, backend, security, and infrastructure capabilities associated with the Ask Red Bear module:")

    t_docx_cap = doc.add_table(rows=1 + len(CAPABILITY_AUDIT_DATA), cols=4)
    t_docx_cap.style = "Table Grid"
    hdr_cells_cap = t_docx_cap.rows[0].cells
    hdr_titles_cap = ["Capability Name", "Technical Implementation", "Current Status", "Operational Scope & Evidence"]
    for idx, name in enumerate(hdr_titles_cap):
        hdr_cells_cap[idx].text = name
        set_cell_background(hdr_cells_cap[idx], PRIMARY_HEX)
        set_cell_margins(hdr_cells_cap[idx], top=60, bottom=60, left=60, right=60)
        p = hdr_cells_cap[idx].paragraphs[0]
        p.runs[0].font.bold = True
        p.runs[0].font.size = Pt(8)
        p.runs[0].font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, cap in enumerate(CAPABILITY_AUDIT_DATA):
        row_cells = t_docx_cap.rows[r_idx + 1].cells
        for c_idx, val in enumerate(cap):
            row_cells[c_idx].text = val
            set_cell_background(row_cells[c_idx], LIGHT_BG_HEX if r_idx % 2 == 1 else "FFFFFF")
            set_cell_margins(row_cells[c_idx], top=40, bottom=40, left=50, right=50)
            p = row_cells[c_idx].paragraphs[0]
            r = p.runs[0]
            r.font.size = Pt(7.5)
            if c_idx == 0 or c_idx == 2:
                r.bold = True

    add_h1("5. TECHNICAL ARCHITECTURE OF AI_GATEWAY.PY AND FAKE_AI_PROVIDER")
    add_body("In the backend repository, backend/app/services/ai_gateway.py establishes an extensible provider pattern:")
    add_code(
"""class AiProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> AiResponse:
        pass

class FakeAiProvider(AiProvider):
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> AiResponse:
        # Returns simulated response for testing
        return AiResponse(
            text=f"This is a simulated Ask Red Bear response to: '{prompt}'. Real AI integration is pending.",
            tokens_used=12,
            model="simulation-stub-v1"
        )"""
    )
    add_body("Because FakeAiProvider is hardcoded as the active instance, all POST requests to /api/v1/ask-red-bear/query return static mocked responses. To activate real AI, an AnthropicClaudeProvider, AzureOpenAiProvider, or Canadian sovereign model class must be instantiated and injected upon Board approval.")

    add_h1("6. PROPOSED RETRIEVAL-AUGMENTED GENERATION (RAG) COMPLETION PIPELINE")
    add_body("To transform Ask Red Bear from a voice dictation tool into an authoritative sovereign policy assistant, the following 6-step engineering pipeline must be executed:")
    for step_title, step_desc in PROPOSED_RAG_PIPELINE:
        add_body(f"• {step_title}: {step_desc}")

    add_h1("7. FIRST NATIONS OCAP® PRINCIPLES & DATA SOVEREIGNTY SAFEGUARDS")
    add_body("Integrating artificial intelligence into a First Nations child welfare agency requires strict adherence to OCAP® (Ownership, Control, Access, and Possession) principles:")
    add_body("• Ownership: Cowessess First Nation retains exclusive intellectual property and ownership over all ingested policies, sacred teachings, and operational data.")
    add_body("• Control: CRBCL leadership controls which documents are ingested, which roles can query them, and what guardrails govern AI responses.")
    add_body("• Access: Frontline staff access is gated by the 327-permission RBAC engine. Caseworkers cannot access information regarding cases where active Case Restrictions exist.")
    add_body("• Possession: Data must reside on Canadian sovereign infrastructure. Enterprise zero-data-retention agreements must ensure commercial AI vendors never train on CRBCL data.")

    add_h1("8. TRANSPARENT CLOUD LLM OPERATING COST PROJECTIONS")
    add_body("To prevent budget surprises, operational token costs have been modeled based on typical enterprise tier rates (e.g., Anthropic Claude 3.5 Sonnet benchmark pricing of $3.00 / million input tokens, $15.00 / million output tokens; final costs depend on Board vendor selection):")
    add_body("• Frontline Staff Assumption: 40 active caseworkers and supervisors conducting an average of 5 policy inquiries per business day = 200 inquiries/day (4,200 inquiries/month).")
    add_body("• Token Consumption per Query: Average 1,500 prompt tokens (user question + retrieved policy context chunks) + 400 completion tokens (synthesized answer).")
    add_body("• Monthly Token Volume: 6.3 million input tokens ($18.90 CAD) + 1.68 million output tokens ($25.20 CAD).")
    add_body("• Vector Index Hosting (PostgreSQL pgvector): $0.00 additional cost (runs natively inside CRBCL's existing managed database container).")
    add_body("• Total Projected AI Operating Cost: Approximately $45.00 to $75.00 CAD per month for the entire organization under regular operational utilization.")

    add_h1("9. PRIORITIZED COMPLETION ROADMAP & GOVERNANCE DECISIONS")
    add_body("To operationalize AI answer generation, the following governance milestones must be achieved:")
    add_body("1. Board Decision: Formal approval of enterprise cloud AI terms of service (zero-data-retention agreement).")
    add_body("2. Knowledge Curation: Executive Director sign-off on the official corpus of policy PDFs for vector ingestion.")
    add_body("3. Infrastructure Deployment: Enablement of pgvector extension on Railway PostgreSQL database.")
    add_body("4. Security Review: Execution of automated prompt injection and case conflict blinding test suites.")
    add_body("5. Supervisor UAT: Structured evaluation workshops with frontline supervisors to test answer accuracy.")

    doc.save(docx_path)
    print(f"Document 4 Revision 2 DOCX written to: {docx_path}")

    # ─────────────────────────────────────────────────────────
    # 2. BUILD PDF (Target 6-10 pages)
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
    story.append(Paragraph("CHIEF RED BEAR CHILDREN'S LODGE<br/>ASK RED BEAR DEVELOPMENT STATUS & COMPLETION ASSESSMENT", styles["CRBCL_CoverTitle"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Evidence-Based Evaluation of Frontline Speech Transcription vs AI Answer Generation<br/>Revision 2 — Clear Operational Differentiation & Sovereign Completion Roadmap", styles["CRBCL_CoverSubtitle"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "<b>Client Organization:</b> Chief Red Bear Children's Lodge / Cowessess First Nation, Saskatchewan, Canada<br/>"
        "<b>Technical Baseline:</b> Post-Phase 5 Hardening | <b>Git Commit HEAD:</b> 0746579 | <b>Branch:</b> main<br/>"
        "<b>Repository Path:</b> C:\\Users\\Shilley Pc\\crbcl | <b>Remote:</b> https://github.com/innovatorledger-web/crbcl<br/>"
        "<b>Audience:</b> CRBCL Board of Directors, Executive Leadership, IT Steering Committee, and Independent Evaluators",
        styles["CRBCL_CoverMeta"]
    ))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=COLOR_PRIMARY, spaceAfter=12))

    notice_text = (
        "<b>Critical Architectural Distinction Notice for CRBCL Leadership:</b> To eliminate any misunderstanding regarding the development status of 'Ask Red Bear', this assessment explicitly separates two fundamentally distinct technical capabilities: (1) Frontline Speech-to-Text Transcription, which converts spoken voice audio into an editable text string inside the user's browser; and (2) AI Answer Generation, which parses natural language questions, searches an organizational knowledge base, and synthesizes intelligent answers. The former is LIVE VERIFIED on the production website; the latter is STUBBED / NOT LIVE via a simulation provider (FakeAiProvider) and has never been connected to a live cloud large language model (LLM)."
    )
    story.append(create_pdf_notice_box_v2("ASK RED BEAR ARCHITECTURAL DISTINCTION", notice_text, styles))
    story.append(PageBreak())

    # Section 1: Executive Summary & Reality
    story.append(Paragraph("1. EXECUTIVE SUMMARY & DEVELOPMENT REALITY", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph(
        "Previous documentation created the impression that Ask Red Bear was an operational artificial intelligence assistant capable of autonomous child welfare practice consultation. A rigorous source-code audit reveals the precise technical reality:",
        styles["CRBCL_Body"]
    ))
    story.append(Paragraph("• <b>Speech-to-Text Dictation is fully implemented and live-verified.</b> When a caseworker clicks the microphone button, audio is recorded, streamed to the backend transcription endpoint, converted into text, and placed into the textarea. No audio recordings or text transcripts are permanently saved to disk, preserving client confidentiality.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Artificial Intelligence Answer Generation is stubbed in source code.</b> In backend/app/services/ai_gateway.py, the active provider is configured as FakeAiProvider. When a user submits a question, the backend returns simulated pre-canned text. There is no active API connection to OpenAI, Anthropic, or any other cloud LLM on production.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Operational Impact:</b> Caseworkers currently possess a highly useful voice dictation tool for drafting progress notes and inquiries, but they do NOT possess an intelligent policy advisory assistant. Full implementation requires Board approval of cloud AI terms, knowledge base curation, and RAG vector infrastructure.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 10))

    # Section 2: Dual-Subsystem Architecture Diagram
    story.append(Paragraph("2. DUAL-SUBSYSTEM ARCHITECTURE & DATA FLOW", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=4))
    story.append(Paragraph("The diagram below illustrates the exact separation between the live speech transcription subsystem and the stubbed AI generation gateway:", styles["CRBCL_Body"]))
    story.append(Spacer(1, 4))
    story.append(create_pdf_diagram_box(ASK_RED_BEAR_ARCHITECTURE_DIAGRAM.strip(), styles, width=540))
    story.append(PageBreak())

    # Section 3: Comparative Matrix Table
    story.append(Paragraph("3. COMPARATIVE ANALYSIS: SPEECH DICTATION VS AI GENERATION", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("The table below compares the two subsystems across all operational, technical, and governance criteria:", styles["CRBCL_Body"]))

    pdf_cmp_rows = [
        [
            Paragraph("<b>Evaluation Dimension</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Speech Dictation (Subsystem A)</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>AI Answer Generation (Subsystem B)</b>", styles["CRBCL_TableHeader"]),
        ]
    ]
    for cmp_row in COMPARISON_MATRIX:
        pdf_cmp_rows.append([
            Paragraph(f"<b>{cmp_row[0]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(cmp_row[1], styles["CRBCL_TableCell"]),
            Paragraph(cmp_row[2], styles["CRBCL_TableCell"]),
        ])

    t_cmp = Table(pdf_cmp_rows, colWidths=[120, 210, 210])
    t_cmp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t_cmp)
    story.append(PageBreak())

    # Section 4: Detailed Capability Audit Table
    story.append(Paragraph("4. DETAILED AUDIT OF 12 ASK RED BEAR CAPABILITIES", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("Below is an audited inventory of all 12 frontend, backend, security, and infrastructure capabilities associated with the Ask Red Bear module:", styles["CRBCL_Body"]))

    pdf_cap_rows = [
        [
            Paragraph("<b>Capability Name</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Implementation Details</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Current Status</b>", styles["CRBCL_TableHeader"]),
            Paragraph("<b>Operational Scope & Evidence</b>", styles["CRBCL_TableHeader"]),
        ]
    ]

    for cap in CAPABILITY_AUDIT_DATA:
        status_color = "#166534" if "LIVE VERIFIED" in cap[2] else ("#991B1B" if "PLANNED" in cap[2] or "STUBBED" in cap[2] else "#1E40AF")
        pdf_cap_rows.append([
            Paragraph(f"<b>{cap[0]}</b>", styles["CRBCL_TableCellBold"]),
            Paragraph(cap[1], styles["CRBCL_TableCell"]),
            Paragraph(f"<font color='{status_color}'><b>{cap[2]}</b></font>", styles["CRBCL_TableCell"]),
            Paragraph(cap[3], styles["CRBCL_TableCell"]),
        ])

    t_cap = Table(pdf_cap_rows, colWidths=[120, 130, 95, 195])
    t_cap.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_PRIMARY),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_LIGHT_BG, colors.white]),
        ("PADDING", (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_cap)
    story.append(PageBreak())

    # Section 5: Technical Architecture of ai_gateway.py
    story.append(Paragraph("5. TECHNICAL ARCHITECTURE OF AI_GATEWAY.PY AND FAKE_AI_PROVIDER", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("In backend/app/services/ai_gateway.py, the system implements an abstract provider interface pattern:", styles["CRBCL_Body"]))
    story.append(create_pdf_diagram_box(
"""class AiProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> AiResponse:
        pass

class FakeAiProvider(AiProvider):
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> AiResponse:
        # Returns simulated response for testing
        return AiResponse(
            text=f"This is a simulated Ask Red Bear response to: '{prompt}'. Real AI integration is pending.",
            tokens_used=12,
            model="simulation-stub-v1"
        )""", styles, width=540
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Because FakeAiProvider is hardcoded as the active instance, all POST requests to /api/v1/ask-red-bear/query return static mocked responses. To activate real AI, an AnthropicClaudeProvider, AzureOpenAiProvider, or Canadian sovereign model class must be instantiated and injected upon Board approval.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 8))

    # Section 6: Proposed RAG Pipeline
    story.append(Paragraph("6. PROPOSED RETRIEVAL-AUGMENTED GENERATION (RAG) COMPLETION PIPELINE", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("To transform Ask Red Bear from a voice dictation tool into an authoritative sovereign policy assistant, the following 6-step engineering pipeline must be executed:", styles["CRBCL_Body"]))
    for step_title, step_desc in PROPOSED_RAG_PIPELINE:
        story.append(Paragraph(f"• <b>{step_title}:</b> {step_desc}", styles["CRBCL_Body"]))
        story.append(Spacer(1, 2))
    story.append(PageBreak())

    # Section 7: First Nations OCAP Principles
    story.append(Paragraph("7. FIRST NATIONS OCAP® PRINCIPLES & DATA SOVEREIGNTY SAFEGUARDS", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("Integrating artificial intelligence into a First Nations child welfare agency requires strict adherence to OCAP® (Ownership, Control, Access, and Possession) principles:", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Ownership:</b> Cowessess First Nation retains exclusive intellectual property and ownership over all ingested policies, sacred teachings, and operational data.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Control:</b> CRBCL leadership controls which documents are ingested, which roles can query them, and what guardrails govern AI responses.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Access:</b> Frontline staff access is gated by the 327-permission RBAC engine. Caseworkers cannot access information regarding cases where active Case Restrictions exist.", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Possession:</b> Data must reside on Canadian sovereign infrastructure. Enterprise zero-data-retention agreements must ensure commercial AI vendors never train on CRBCL data.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 8))

    # Section 8: Cloud LLM Operating Cost Projections
    story.append(Paragraph("8. TRANSPARENT CLOUD LLM OPERATING COST PROJECTIONS", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("To prevent budget surprises, operational token costs have been modeled based on typical enterprise tier rates (e.g., Anthropic Claude 3.5 Sonnet benchmark pricing of $3.00 / million input tokens, $15.00 / million output tokens; final costs depend on Board vendor selection):", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Frontline Staff Assumption:</b> 40 active caseworkers and supervisors conducting an average of 5 policy inquiries per business day = 200 inquiries/day (4,200 inquiries/month).", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Token Consumption per Query:</b> Average 1,500 prompt tokens (user question + retrieved policy context chunks) + 400 completion tokens (synthesized answer).", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Monthly Token Volume:</b> 6.3 million input tokens ($18.90 CAD) + 1.68 million output tokens ($25.20 CAD).", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Vector Index Hosting (PostgreSQL pgvector):</b> $0.00 additional cost (runs natively inside CRBCL's existing managed database container).", styles["CRBCL_Body"]))
    story.append(Paragraph("• <b>Total Projected AI Operating Cost:</b> Approximately <b>$45.00 to $75.00 CAD per month</b> for the entire organization under regular operational utilization.", styles["CRBCL_Body"]))
    story.append(Spacer(1, 8))

    # Section 9: Prioritized Roadmap & Decisions
    story.append(Paragraph("9. PRIORITIZED COMPLETION ROADMAP & GOVERNANCE DECISIONS", styles["CRBCL_H1"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_PRIMARY, spaceAfter=6))
    story.append(Paragraph("To operationalize AI answer generation, the following governance milestones must be achieved:", styles["CRBCL_Body"]))
    story.append(Paragraph("1. <b>Board Decision:</b> Formal approval of enterprise cloud AI terms of service (zero-data-retention agreement).", styles["CRBCL_Body"]))
    story.append(Paragraph("2. <b>Knowledge Curation:</b> Executive Director sign-off on the official corpus of policy PDFs for vector ingestion.", styles["CRBCL_Body"]))
    story.append(Paragraph("3. <b>Infrastructure Deployment:</b> Enablement of pgvector extension on Railway PostgreSQL database.", styles["CRBCL_Body"]))
    story.append(Paragraph("4. <b>Security Review:</b> Execution of automated prompt injection and case conflict blinding test suites.", styles["CRBCL_Body"]))
    story.append(Paragraph("5. <b>Supervisor UAT:</b> Structured evaluation workshops with frontline supervisors to test answer accuracy.", styles["CRBCL_Body"]))

    pdf_doc.build(story, canvasmaker=NumberedCanvasV2)
    print(f"Document 4 Revision 2 PDF written to: {pdf_path}")
    return docx_path, pdf_path


if __name__ == "__main__":
    build_doc4()
