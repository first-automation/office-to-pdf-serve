# office-to-pdf-serve

Convert an Office document (xlsx, docx, pptx) to a PDF file.

## Quick Start

Installation

```bash
sudo apt install libreoffice
git clone https://github.com/first-automation/office-to-pdf-serve.git
cd office-to-pdf-serve
uv sync
```

Start the servers.

```bash
soffice --accept="socket,host=localhost,port=2002;urp;StarOffice.ServiceManager" --headless
# in another terminal
uv run fastapi run app.py
```

Or use docker compose to run the services.

```bash
cd office-to-pdf-serve
cp .env.example .env
docker compose up
```

Convert a file to PDF.

```bash
curl -X 'POST' \
'http://localhost:8000/convert_to_pdf' \
-H 'accept: application/json' \
-H 'Content-Type: multipart/form-data' \
-F 'file=@path/to/file.xlsx'
```

Or you can use the web UI at http://localhost:8000/docs.

## Deploy to Cloud Run

```bash
gcloud auth login
gcloud config set project <project_id>
export CLOUDRUN_LOCATION=asia-northeast1
export CLOUDRUN_SERVICE_ACCOUNT_NAME=<your_service_account_name>
export DOCKER_IMAGE_URL=<your_docker_image_url>
gcloud builds submit --tag ${DOCKER_IMAGE_URL}
envsubst < gcloud/cloudrun.yaml.in > gcloud/cloudrun.yaml
gcloud run services replace gcloud/cloudrun.yaml --region=${CLOUDRUN_LOCATION}
```
