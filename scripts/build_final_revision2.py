"""
CRBCL -- Master Final Build Script
Regenerates all Revision 2 documents with all corrections applied, then
creates the Board_Distribution_Package and performs final QA.

Corrections applied:
  - Doc1: Mobile offline status updated to developer-confirmed (already in source)
  - Doc3: Mobile feature entries updated (already in source), Sprint 3 roadmap fix
  - Private Commercial doc: generated separately in Private folder
  - Board Distribution Package: created with exactly 8 Board-facing files
"""

import os
import sys
import shutil
import subprocess

# ─── Ensure backend app is importable ───
sys.path.insert(0, r"C:\Users\Shilley Pc\crbcl")
sys.path.insert(0, r"C:\Users\Shilley Pc\crbcl\backend")

from scripts.deliverables_generator_v2.doc1_board_report_v2 import build_doc1
from scripts.deliverables_generator_v2.doc2_tech_architecture_v2 import build_doc2
from scripts.deliverables_generator_v2.doc3_feature_register_v2 import build_doc3
from scripts.deliverables_generator_v2.doc4_ask_red_bear_v2 import build_doc4
from scripts.deliverables_generator_v2.doc_private_commercial import build_private_commercial_doc

DELIVERABLES_V2_DIR = os.path.join(
    r"C:\Users\Shilley Pc\crbcl",
    "deliverables",
    "CRBCL_Board_Update_October_2026",
    "Revision_2"
)

BOARD_DISTRIBUTION_DIR = os.path.join(DELIVERABLES_V2_DIR, "Board_Distribution_Package")

PRIVATE_DIR = os.path.join(
    r"C:\Users\Shilley Pc\crbcl",
    "deliverables",
    "CRBCL_Private_Developer_Commercial_Correspondence_October_2026"
)


def fix_doc3_sprint3():
    """Directly patch Sprint 3 text in doc3 source if it still contains old text."""
    doc3_path = r"C:\Users\Shilley Pc\crbcl\scripts\deliverables_generator_v2\doc3_feature_register_v2.py"
    with open(doc3_path, "r", encoding="utf-8") as f:
        content = f.read()

    old = (
        '(2) Device-level offline field UAT for the Flutter mobile application in rural Cowessess communities; '
        '(3) Multi-user browser offline testing before enabling CRBCL_OFFLINE_WEB_ENABLED.'
    )
    new = (
        '(2) Organizational supervisor-level field UAT for the Flutter mobile application '
        '(developer offline confirmation complete; sync/conflict/recovery scenarios to be validated '
        'with CRBCL frontline supervisors); '
        '(3) Multi-user browser offline testing before enabling CRBCL_OFFLINE_WEB_ENABLED.'
    )

    if old in content:
        content = content.replace(old, new)
        with open(doc3_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[OK] Doc3 Sprint 3 roadmap text patched.")
    elif new in content:
        print("[OK] Doc3 Sprint 3 already patched -- no change needed.")
    else:
        print("[WARN] Doc3 Sprint 3 patch: target text not found -- check manually.")


def build_all():
    print("=" * 70)
    print("CRBCL REVISION 2 -- MASTER FINAL BUILD")
    print("=" * 70)
    print()

    # ── Pre-build patches ──────────────────────────────────────────────
    print("Step 1/7: Applying remaining source patches ...")
    fix_doc3_sprint3()
    print()

    # ── Build Board Documents ──────────────────────────────────────────
    print("Step 2/7: Generating Document 1 -- Board Progress Report ...")
    d1_docx, d1_pdf = build_doc1()
    print()

    print("Step 3/7: Generating Document 2 -- Technical Architecture ...")
    d2_docx, d2_pdf = build_doc2()
    print()

    print("Step 4/7: Generating Document 3 -- Feature Register ...")
    d3_docx, d3_pdf = build_doc3()
    print()

    print("Step 5/7: Generating Document 4 -- Ask Red Bear Assessment ...")
    d4_docx, d4_pdf = build_doc4()
    print()

    # ── Build Private Commercial Doc ───────────────────────────────────
    print("Step 6/7: Generating Private Commercial Correspondence ...")
    priv_docx, priv_pdf = build_private_commercial_doc()
    print()

    # ── Create Board Distribution Package ─────────────────────────────
    print("Step 7/7: Creating Board_Distribution_Package ...")
    os.makedirs(BOARD_DISTRIBUTION_DIR, exist_ok=True)

    board_files = [d1_docx, d1_pdf, d2_docx, d2_pdf, d3_docx, d3_pdf, d4_docx, d4_pdf]
    for src in board_files:
        dst = os.path.join(BOARD_DISTRIBUTION_DIR, os.path.basename(src))
        shutil.copy2(src, dst)
        print(f"  Copied: {os.path.basename(src)}")

    # Confirm private doc is NOT in board package
    priv_name = os.path.basename(priv_docx)
    board_filenames = [os.path.basename(f) for f in board_files]
    assert priv_name not in board_filenames, "CRITICAL: Private doc found in Board file list!"
    priv_in_board_dir = os.path.join(BOARD_DISTRIBUTION_DIR, priv_name)
    assert not os.path.exists(priv_in_board_dir), "CRITICAL: Private doc copied to Board folder!"
    print("  [OK] Private commercial document confirmed ABSENT from Board_Distribution_Package.")
    print()

    # ── QA: pypdf page count verification ─────────────────────────────
    try:
        import pypdf
        print("=" * 70)
        print("FINAL QA: PDF PAGE COUNT VERIFICATION")
        print("=" * 70)
        all_pdfs = [
            ("Doc 1 -- Board Progress Report", d1_pdf),
            ("Doc 2 -- Technical Architecture", d2_pdf),
            ("Doc 3 -- Feature Register", d3_pdf),
            ("Doc 4 -- Ask Red Bear Assessment", d4_pdf),
            ("Private Commercial Correspondence", priv_pdf),
        ]
        total_board_pages = 0
        payment_terms = ["2500", "2,500", "2200", "2,200", "CAD $2", "original quotation", "compensation discussion", "developer fee"]
        issues = []

        for label, pdf_path in all_pdfs:
            reader = pypdf.PdfReader(pdf_path)
            pages = len(reader.pages)
            size_kb = os.path.getsize(pdf_path) // 1024

            # Scan Board docs for payment terms
            is_board = "Private" not in label
            if is_board:
                full_text = ""
                for pg in reader.pages:
                    full_text += pg.extract_text() or ""
                found = [t for t in payment_terms if t.lower() in full_text.lower()]
                if found:
                    issues.append(f"  [WARN] PAYMENT REFERENCE FOUND in {label}: {found}")
                else:
                    pass
                total_board_pages += pages

            # Check mobile offline language in Board docs
            if is_board:
                full_text_check = ""
                for pg in reader.pages:
                    full_text_check += pg.extract_text() or ""
                if "mobile" in full_text_check.lower() and "offline" in full_text_check.lower():
                    has_confirmed = "firsthand" in full_text_check.lower() or "confirmed" in full_text_check.lower() or "developer" in full_text_check.lower()
                    mobile_status = "[OK] DEVELOPER-CONFIRMED language present" if has_confirmed else "[WARN] Mobile offline language found but may not reflect confirmation"
                else:
                    mobile_status = "(mobile offline not mentioned in this doc)"
                print(f"  {label}: {pages} pages | {size_kb} KB | Mobile: {mobile_status}")
            else:
                print(f"  {label}: {pages} pages | {size_kb} KB | [PRIVATE -- not scanned for Board content]")

        print()
        print(f"  Total Board document pages: {total_board_pages}")

        if issues:
            print()
            print("  ISSUES FOUND:")
            for issue in issues:
                print(issue)
        else:
            print("  [OK] All Board PDFs: CLEAN -- no payment/compensation dollar references found.")

        # Confirm private doc not in board distribution
        board_dist_files = os.listdir(BOARD_DISTRIBUTION_DIR)
        private_doc_base = os.path.basename(priv_pdf)
        if private_doc_base in board_dist_files or os.path.basename(priv_docx) in board_dist_files:
            print("  [WARN] CRITICAL: Private document found in Board_Distribution_Package!")
        else:
            print(f"  [OK] Board_Distribution_Package contains {len(board_dist_files)} files -- private commercial doc ABSENT.")

        print()
        print("=" * 70)
        print("BUILD COMPLETE")
        print("=" * 70)
        print(f"  Board Docs (8 files)  -> {DELIVERABLES_V2_DIR}")
        print(f"  Board Package (8 files) -> {BOARD_DISTRIBUTION_DIR}")
        print(f"  Private Correspondence -> {PRIVATE_DIR}")
        print()

    except ImportError:
        print("pypdf not available -- skipping PDF QA scan.")

    return {
        "board": [d1_docx, d1_pdf, d2_docx, d2_pdf, d3_docx, d3_pdf, d4_docx, d4_pdf],
        "private": [priv_docx, priv_pdf],
        "board_dist": BOARD_DISTRIBUTION_DIR,
    }


if __name__ == "__main__":
    build_all()
