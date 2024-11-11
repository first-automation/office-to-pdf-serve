# office-to-pdf-serve

Convert an Office document to a PDF file.

## Quick Start

```bash
sudo apt install libreoffice
soffice --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" --headless
# in another terminal
fastapi run app.py
```

Or use docker compose to run the services.

```bash
docker compose up
```

Convert a file to PDF.

```bash
curl -X POST -F "file=@path/to/file.xlsx" http://localhost:8000/convert_to_pdf
```
