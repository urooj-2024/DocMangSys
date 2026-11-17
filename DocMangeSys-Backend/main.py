from fastapi import FastAPI, HTTPException, UploadFile, File, Form  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from db import get_connection
import uuid
import io
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "DMS is working ✅"}

@app.post("/documents")
async def create_document(
    title: str    = Form(...),
    content: str  = Form(...),
    file: UploadFile = File(...)
):
    file_bytes = await file.read()
    file_name = file.filename

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (title, content, file_name, file_data)
            VALUES (%s, %s, %s, %s)
            """,
            (title, content, file_name, file_bytes)
        )
        conn.commit()

        # Get the inserted document ID
        doc_id = cursor.lastrowid

    except Exception as e:
        raise HTTPException(500, f"Error saving document: {e}")
    finally:
        cursor.close()
        conn.close()

    return {
        "message": "Document uploaded and saved in DB ✅",
        "id": doc_id,
        "title": title,
        "file_name": file_name
    }

@app.get("/documents")
def get_documents():
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, title, content, file_name FROM documents")
            docs = cursor.fetchall()
    finally:
        conn.close()
    return docs

@app.get("/documents/{doc_id}")
def get_document_metadata(doc_id: int):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute(
                "SELECT id, title, content, file_name FROM documents WHERE id = %s",
                (doc_id,)
            )
            row = cursor.fetchone()
    finally:
        conn.close()

    if not row:
        raise HTTPException(404, "Document not found")
    return row

@app.get("/documents/{doc_id}/download")
def download_document(doc_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT file_name, file_data FROM documents WHERE id = %s",
                (doc_id,)
            )
            result = cursor.fetchone()
    finally:
        conn.close()

    if not result:
        raise HTTPException(404, "Document not found")

    file_name, blob = result
    return StreamingResponse(
        io.BytesIO(blob),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: int):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM documents WHERE id = %s", (doc_id,))
            conn.commit()
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        conn.close()

    return {"message": "Document deleted successfully"}

@app.put("/documents/{doc_id}")
async def update_document(
    doc_id: int,
    title: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM documents WHERE id = %s", (doc_id,))
            current = cursor.fetchone()
            if not current:
                raise HTTPException(404, "Document not found")

            new_title = title or current["title"]
            new_content = content or current["content"]

            if file:
                new_file_name = file.filename
                new_file_bytes = await file.read()
            else:
                new_file_name = current["file_name"]
                new_file_bytes = current["file_data"]

            cursor.execute(
                """
                UPDATE documents
                SET title = %s, content = %s, file_name = %s, file_data = %s
                WHERE id = %s
                """,
                (new_title, new_content, new_file_name, new_file_bytes, doc_id)
            )
            conn.commit()
    except Exception as e:
        raise HTTPException(500, str(e))
    finally:
        conn.close()

    return {"message": "Document updated successfully ✅"}
