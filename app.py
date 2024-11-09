import os
import sys
sys.path.append(os.getenv("UNO_PACKAGE_PATH"))

from office_to_pdf_serve.api import create_app

app = create_app()
