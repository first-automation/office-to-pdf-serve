import aiofiles
import os
import io
import tempfile
from typing import Literal

import uno
from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from office_to_pdf_serve.office_client import OfficeClient

SupportedFileTypes = Literal["xlsx", "docx", "pptx"]


router = APIRouter()


@router.post("/convert_to_pdf")
async def convert_to_pdf(file: UploadFile = File(...)):
    os.makedirs("/tmp/office-to-pdf-serve", exist_ok=True)
    file_type = os.path.splitext(file.filename)[1]
    if file_type not in SupportedFileTypes.__args__:
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type: {file_type}"
        )
    excel_filename = tempfile.mktemp(suffix=file_type, dir="/tmp/office-to-pdf-serve")
    pdf_filename = tempfile.mktemp(suffix=".pdf", dir="/tmp/office-to-pdf-serve")
    contents = await file.read()
    async with aiofiles.open(excel_filename, "wb") as buffer:
        await buffer.write(contents)
    input_url = uno.systemPathToFileUrl(os.path.abspath(excel_filename))
    output_url = uno.systemPathToFileUrl(os.path.abspath(pdf_filename))

    try:
        client = OfficeClient(
            os.getenv("LIBREOFFICE_HOSTNAME"), os.getenv("LIBREOFFICE_PORT")
        )
        client.load_document(input_url)
        if file_type == ".xlsx":
            client.update_print_areas()
        client.export_to_pdf(output_url)
        client.close_document()

        pdf_bytes = io.BytesIO()
        with open(pdf_filename, "rb") as buffer:
            pdf_bytes.write(buffer.read())
        pdf_bytes.seek(0)
        return StreamingResponse(pdf_bytes, media_type="application/pdf")
    finally:
        os.remove(excel_filename)
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)


def create_app():
    app = FastAPI()
    app.include_router(router)
    return app
