import os
import fitz
from docx import Document
from backend.app.core.config import settings

SAMPLE_DIR = os.path.join(settings.DATA_DIR, "sample_docs")
os.makedirs(SAMPLE_DIR, exist_ok=True)

def create_sample_academic_regulations():
    pdf_path = os.path.join(SAMPLE_DIR, "academic_regulations_2026.pdf")
    doc = fitz.open()

    # Page 1
    p1 = doc.new_page()
    p1.insert_text((50, 60), "NATIONAL INSTITUTE OF TECHNOLOGY & HIGHER STUDIES", fontsize=14)
    p1.insert_text((50, 85), "ACADEMIC REGULATIONS & POLICIES (2026-2027)", fontsize=12)
    p1.insert_text((50, 120), "Chapter 1: Enrollment and Academic Conduct\n\n"
                              "1.1 Scope and Application:\n"
                              "These regulations apply to all undergraduate (B.Tech, B.Sc) and postgraduate (M.Tech, MCA, MBA)\n"
                              "degree programmes offered by the University.\n\n"
                              "1.2 Registration:\n"
                              "Every student must register for prescribed courses at the beginning of each semester on the\n"
                              "dates announced in the Academic Calendar. Late registration with penalty is permitted up to 7 days.", fontsize=10)

    # Page 2
    p2 = doc.new_page()
    p2.insert_text((50, 60), "Chapter 2: Attendance Requirements & Examination Eligibility", fontsize=12)
    p2.insert_text((50, 95), "Rule 4.1 Attendance Threshold:\n"
                             "Every enrolled student must maintain a minimum attendance of 75% in all lectures, tutorials,\n"
                             "and practical classes to be eligible to appear for the end-semester examinations.\n\n"
                             "Rule 4.2 Medical Condonation:\n"
                             "A condonation of attendance up to 10% (relaxing the minimum requirement to 65%) may be granted\n"
                             "by the Academic Dean strictly on documented medical grounds or authorized participation in\n"
                             "state/national university sports or cultural events. Medical certificates must be submitted\n"
                             "within 7 working days of returning to classes.\n\n"
                             "Rule 4.3 Debarment:\n"
                             "Students with attendance below 65% under any circumstances shall be debarred from writing the\n"
                             "end-semester examination in that course and must re-register when the course is offered next.", fontsize=10)

    # Page 3
    p3 = doc.new_page()
    p3.insert_text((50, 60), "Chapter 3: Grading System and Revaluation Policy", fontsize=12)
    p3.insert_text((50, 95), "3.1 Grading Scale:\n"
                             "Academic evaluation is recorded on a 10-point letter grade system:\n"
                             "  - Grade O (Outstanding): 10 grade points (90% and above)\n"
                             "  - Grade A+ (Excellent): 9 grade points (80% to 89%)\n"
                             "  - Grade A (Very Good): 8 grade points (70% to 79%)\n"
                             "  - Grade B+ (Good): 7 grade points (60% to 69%)\n"
                             "  - Grade B (Above Average): 6 grade points (50% to 59%)\n"
                             "  - Grade C (Average): 5 grade points (45% to 49%)\n"
                             "  - Grade P (Pass): 4 grade points (40% to 44%)\n"
                             "  - Grade F (Fail): 0 grade points (Below 40%)\n\n"
                             "3.2 Revaluation & Answer Script Inspection:\n"
                             "A student who is dissatisfied with their grade in any theory course may apply for revaluation\n"
                             "within 14 calendar days from the date of online result announcement.\n"
                             "The non-refundable revaluation fee is Rs. 500 per course paper.", fontsize=10)

    doc.save(pdf_path)
    doc.close()
    print("Created academic_regulations_2026.pdf")

def create_sample_exam_notice():
    pdf_path = os.path.join(SAMPLE_DIR, "examination_circular_nov2026.pdf")
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 60), "OFFICE OF THE CONTROLLER OF EXAMINATIONS", fontsize=14)
    p1.insert_text((50, 85), "CIRCULAR: END-SEMESTER EXAMINATIONS - NOVEMBER 2026", fontsize=12)
    p1.insert_text((50, 110), "Circular No: EXAM/2026/CIRC/104 | Date of Notice: 10th November 2026", fontsize=9)
    p1.insert_text((50, 140), "Audience: All 2nd Year, 3rd Year, and 4th Year B.Tech and MCA Students\n\n"
                              "1. Examination Schedule:\n"
                              "End-Semester Theory Examinations for odd semesters (Semesters 3, 5, and 7) will commence\n"
                              "from 15th December 2026 across all university examination centers.\n\n"
                              "2. Registration Form and Fee Deadlines:\n"
                              "All eligible students must submit their online examination enrollment form and verify payment\n"
                              "on or before 25th November 2026 without any late fee penalty.\n\n"
                              "Late registration with an additional penalty fee of Rs. 1000 will be permitted between\n"
                              "26th November 2026 and 30th November 2026.\n"
                              "NO EXAMINATION FORMS WILL BE ACCEPTED AFTER 30th NOVEMBER 2026.\n\n"
                              "3. Hall Ticket Issuance:\n"
                              "Admit cards/hall tickets will be released on the student portal on 5th December 2026.\n"
                              "Students must bring their physical university ID card along with printed hall ticket.", fontsize=10)
    doc.save(pdf_path)
    doc.close()
    print("Created examination_circular_nov2026.pdf")

def create_sample_docx():
    docx_path = os.path.join(SAMPLE_DIR, "hostel_and_mess_regulations_2026.docx")
    doc = Document()
    doc.add_heading("University Student Residential & Hostel Regulations", 0)
    doc.add_paragraph("Office of the Dean of Student Welfare (DSW)")
    
    doc.add_heading("1. Mess Fee Schedule and Dues", level=1)
    doc.add_paragraph("Hostel residents must remit monthly mess charges by the 10th of each calendar month. "
                      "A late fine of Rs. 50 per day will be levied after the 10th. Continuous non-payment for two "
                      "months will lead to forfeiture of hostel allotment.")
    
    doc.add_heading("2. Hostel Timings and Night Passes", level=1)
    doc.add_paragraph("All hostel gates will be locked strictly at 9:30 PM. Students requiring late entry for academic "
                      "library projects must obtain prior written approval from their hostel warden by 6:00 PM.")

    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Item"
    hdr_cells[1].text = "Amount (INR)"
    hdr_cells[2].text = "Due Date"
    
    row1 = table.add_row().cells
    row1[0].text = "Mess Fee (Monthly)"
    row1[1].text = "Rs. 4,500"
    row1[2].text = "10th of every month"

    row2 = table.add_row().cells
    row2[0].text = "Hostel Caution Deposit (Refundable)"
    row2[1].text = "Rs. 10,000"
    row2[2].text = "At time of admission"

    doc.save(docx_path)
    print("Created hostel_and_mess_regulations_2026.docx")

if __name__ == "__main__":
    create_sample_academic_regulations()
    create_sample_exam_notice()
    create_sample_docx()
