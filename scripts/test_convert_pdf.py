import os
import argparse
import sys
sys.path.append("/usr/lib/python3/dist-packages/")

from office_to_pdf_serve.office_client import OfficeClient


parser = argparse.ArgumentParser()
parser.add_argument("input_file")
parser.add_argument("output_file")
args = parser.parse_args()

input_url = f"file://{os.path.abspath(args.input_file)}"
output_url = f"file://{os.path.abspath(args.output_file)}"

client = OfficeClient()
client.load_document(input_url)
client.update_print_areas()
client.export_to_pdf(output_url)
client.close_document()
