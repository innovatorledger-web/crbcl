"""Final QA verification for CRBCL Revision 2 document package."""
import pypdf
import os
import subprocess

print('=' * 68)
print('CRBCL REVISION 2 -- FINAL COMPREHENSIVE QA REPORT')
print('=' * 68)

BASE = r'C:\Users\Shilley Pc\crbcl'
BOARD_DIR = os.path.join(BASE, 'deliverables', 'CRBCL_Board_Update_October_2026', 'Revision_2')
DIST_DIR = os.path.join(BOARD_DIR, 'Board_Distribution_Package')
PRIVATE_DIR = os.path.join(BASE, 'deliverables', 'CRBCL_Private_Developer_Commercial_Correspondence_October_2026')

board_pdfs = [
    'CRBCL_Comprehensive_Platform_Development_Progress_Report_Revision_2_October_2026.pdf',
    'CRBCL_Updated_Technical_Architecture_and_Development_Documentation_Revision_2_October_2026.pdf',
    'CRBCL_Feature_Completion_and_Remaining_Work_Register_Revision_2_October_2026.pdf',
    'CRBCL_Ask_Red_Bear_Development_Status_and_Completion_Assessment_Revision_2_October_2026.pdf',
]

priv_pdf = 'CRBCL_Private_Original_Agreement_Additional_Development_and_Compensation_Discussion_October_2026.pdf'
priv_docx = 'CRBCL_Private_Original_Agreement_Additional_Development_and_Compensation_Discussion_October_2026.docx'

payment_terms = ['2500', '2,500', '2200', '2,200', 'original quotation', 'compensation discussion', 'developer fee']
mobile_confirmed_terms = ['firsthand', 'physically tested', 'personally tested', 'developer confirms', 'developer-confirmed', 'developer installed']
mobile_confirm_label = 'developer-confirmed'

print()
print('PART A: BOARD DOCUMENTS')
print('-' * 68)
total_board_pages = 0
for i, fname in enumerate(board_pdfs, 1):
    fpath = os.path.join(BOARD_DIR, fname)
    if not os.path.exists(fpath):
        print('  [MISSING] ' + fname)
        continue
    reader = pypdf.PdfReader(fpath)
    pages = len(reader.pages)
    total_board_pages += pages
    size_kb = os.path.getsize(fpath) // 1024
    full_text = ''.join(pg.extract_text() or '' for pg in reader.pages).lower()

    pay_found = [t for t in payment_terms if t.lower() in full_text]
    mobile_has_offline = 'offline' in full_text and 'mobile' in full_text
    mobile_confirmed = any(t.lower() in full_text for t in mobile_confirmed_terms)

    pay_status = '[OK] CLEAN' if not pay_found else '[WARN] Found: ' + str(pay_found)
    if mobile_confirmed:
        mob_status = '[OK] Developer-confirmed wording present'
    elif mobile_has_offline:
        mob_status = '[INFO] Mobile offline mentioned; check confirmation language'
    else:
        mob_status = '[INFO] Mobile offline not discussed in this doc'

    short_name = fname[:58] + '...' if len(fname) > 58 else fname
    print('  Doc ' + str(i) + ': ' + str(pages) + ' pages | ' + str(size_kb) + ' KB')
    print('    ' + short_name)
    print('    Payment refs: ' + pay_status)
    print('    Mobile status: ' + mob_status)
    print()

print('  Total Board pages: ' + str(total_board_pages))
print()

print('PART B: BOARD DISTRIBUTION PACKAGE')
print('-' * 68)
if os.path.exists(DIST_DIR):
    dist_files = sorted(os.listdir(DIST_DIR))
    print('  Files in package: ' + str(len(dist_files)))
    for f in dist_files:
        size = os.path.getsize(os.path.join(DIST_DIR, f)) // 1024
        print('    ' + f[:65] + ' (' + str(size) + ' KB)')
    priv_in_dist = any('Private' in f or 'Original_Agreement' in f for f in dist_files)
    if priv_in_dist:
        print('  [WARN] PRIVATE DOCUMENT FOUND IN BOARD PACKAGE -- REVIEW REQUIRED')
    else:
        print('  [OK] Private commercial document is ABSENT from Board Distribution Package.')
else:
    print('  [MISSING] Board_Distribution_Package directory not found.')

print()
print('PART C: PRIVATE COMMERCIAL CORRESPONDENCE')
print('-' * 68)
priv_fpath = os.path.join(PRIVATE_DIR, priv_pdf)
priv_dpath = os.path.join(PRIVATE_DIR, priv_docx)

if os.path.exists(priv_fpath):
    reader = pypdf.PdfReader(priv_fpath)
    pages = len(reader.pages)
    size_kb = os.path.getsize(priv_fpath) // 1024
    full_text = ''.join(pg.extract_text() or '' for pg in reader.pages).lower()
    has_2500 = '2,500' in full_text or '2500' in full_text
    has_2200 = '2,200' in full_text or '2200' in full_text
    has_300 = '300' in full_text
    docx_ok = os.path.exists(priv_dpath)
    print('  PDF: ' + str(pages) + ' pages | ' + str(size_kb) + ' KB')
    print('  Contains CAD 2500: ' + ('[OK]' if has_2500 else '[WARN] Missing'))
    print('  Contains CAD 2200: ' + ('[OK]' if has_2200 else '[WARN] Missing'))
    print('  Contains 300 balance: ' + ('[OK]' if has_300 else '[WARN] Missing'))
    print('  DOCX exists: ' + ('[OK]' if docx_ok else '[MISSING]'))
    print('  Location: ' + PRIVATE_DIR)
else:
    print('  [MISSING] ' + priv_fpath)

print()
print('PART D: GIT STATUS CHECK')
print('-' * 68)
res = subprocess.run(['git', 'log', '--oneline', '-3'], capture_output=True, text=True, cwd=BASE)
print('  Recent commits:')
for line in res.stdout.strip().split('\n'):
    print('    ' + line)
res2 = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True, cwd=BASE)
app_changes = [l for l in res2.stdout.strip().split('\n')
               if l and not any(x in l for x in ['deliverables/', 'scripts/'])]
if [c for c in app_changes if c.strip()]:
    print('  [WARN] Application file changes detected:')
    for c in app_changes[:10]:
        if c.strip():
            print('    ' + c)
else:
    print('  [OK] No application source changes (only deliverables/ and scripts/ modified).')

print()
print('=' * 68)
print('QA COMPLETE')
print('=' * 68)
