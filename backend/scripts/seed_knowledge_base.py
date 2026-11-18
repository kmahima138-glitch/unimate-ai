import os
import shutil
from backend.app.core.config import settings
from backend.app.db.database import db
from backend.app.services.document_ingestion import document_ingestion_service
from backend.app.services.notice_service import notice_service

SAMPLE_DIR = os.path.join(settings.DATA_DIR, "sample_docs")

def seed():
    print("Initializing database...")
    db.init_db()

    docs = [
        {
            "filename": "academic_regulations_2026.pdf",
            "title": "Academic Regulations & Policies 2026",
            "category": "academic",
            "file_type": "PDF"
        },
        {
            "filename": "examination_circular_nov2026.pdf",
            "title": "End-Semester Examination Circular Nov 2026",
            "category": "examination",
            "file_type": "PDF"
        },
        {
            "filename": "hostel_and_mess_regulations_2026.docx",
            "title": "Hostel & Mess Regulations 2026",
            "category": "general",
            "file_type": "DOCX"
        }
    ]

    for item in docs:
        src = os.path.join(SAMPLE_DIR, item["filename"])
        if not os.path.exists(src):
            print(f"Skipping {src}, not found")
            continue

        size = os.path.getsize(src)
        print(f"Ingesting {item['title']} ({item['filename']})...")
        doc_id = document_ingestion_service.create_pending_document(
            filename=item["filename"],
            title=item["title"],
            category=item["category"],
            file_type=item["file_type"],
            file_size=size,
            uploaded_by="System Seeder"
        )

        dest = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{item['filename']}")
        shutil.copy(src, dest)

        res = document_ingestion_service.process_document(doc_id, dest, item["category"])
        print(f"  -> Indexed: {res['chunk_count']} chunks across {res['page_count']} pages.")

        # Extract notice if circular
        if item["category"] == "examination":
            with open(src, "rb") as f:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT text FROM document_chunks WHERE document_id = ?", (doc_id,))
                    text_blob = " ".join([r["text"] for r in cursor.fetchall()])
                    notice_service.extract_and_publish_notice(
                        title=item["title"],
                        content=text_blob,
                        document_id=doc_id,
                        category="examination"
                    )
            print("  -> Extracted & published official examination circular notice.")

    print("\nKnowledge base successfully seeded!")

if __name__ == "__main__":
    seed()
