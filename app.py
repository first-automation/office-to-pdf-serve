import os
import sys
sys.path.append(os.getenv("UNO_PACKAGE_PATH", "/usr/lib/python3/dist-packages/"))

from office_to_pdf_serve.api import create_app

app = create_app()
