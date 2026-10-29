"""Scan Board PDFs for payment-related references that must be removed."""
import pypdf
import os

payment_terms = ['2500', '2,500', '2200', '2,200', 'quotation', 'compensation', 'payment', 'CAD $', 'developer fee', 'hired', 'negotiat']

board_pdfs = [
    'deliverables/CRBCL_Board_Update_October_2026/Revision_2/CRBCL_Comprehensive_Platform_Development_Progress_Report_Revision_2_October_2026.pdf',
    'deliverables/CRBCL_Board_Update_October_2026/Revision_2/CRBCL_Updated_Technical_Architecture_and_Development_Documentation_Revision_2_October_2026.pdf',
    'deliverables/CRBCL_Board_Update_October_2026/Revision_2/CRBCL_Feature_Completion_and_Remaining_Work_Register_Revision_2_October_2026.pdf',
    'deliverables/CRBCL_Board_Update_October_2026/Revision_2/CRBCL_Ask_Red_Bear_Development_Status_and_Completion_Assessment_Revision_2_October_2026.pdf',
]

print('=== SCANNING BOARD PDFs FOR PAYMENT REFERENCES ===')
for pdf_path in board_pdfs:
    reader = pypdf.PdfReader(pdf_path)
    full_text = ''
    for page in reader.pages:
        full_text += page.extract_text() or ''
    found_terms = []
    for term in payment_terms:
        if term.lower() in full_text.lower():
            found_terms.append(term)
    short_name = os.path.basename(pdf_path)[:60]
    if found_terms:
        print(f'ISSUES FOUND in {short_name}:')
        for t in found_terms:
            print(f'  - Contains: "{t}"')
    else:
        print(f'CLEAN: {short_name}')

print('')
print('=== MOBILE OFFLINE STATUS CHECK ===')
for pdf_path in board_pdfs:
    reader = pypdf.PdfReader(pdf_path)
    full_text = ''
    for page in reader.pages:
        full_text += page.extract_text() or ''
    has_mobile = 'offline' in full_text.lower() and 'mobile' in full_text.lower()
    short_name = os.path.basename(pdf_path)[:60]
    print(f'{short_name}: mobile offline mentioned = {has_mobile}')
