import aiofiles
import os
import io
import tempfile

import uno
from fastapi import APIRouter, FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse

from office_to_pdf_serve.office_client import OfficeClient


router = APIRouter()


@router.post("/convert_to_pdf")
async def convert_to_pdf(file: UploadFile = File(...)):
    os.makedirs("/tmp/office-to-pdf-serve", exist_ok=True)
    excel_filename = tempfile.mktemp(suffix=".xlsx", dir="/tmp/office-to-pdf-serve")
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
