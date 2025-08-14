# SinglePageSheets対応、本来であればuno経由でやるべきだが、
# うまくいかなかったため、CLI経由で行う
import os
import subprocess

def convert_to_pdf_single_page(input_file_path: str, output_file_path: str) -> None:
    convert_to = "pdf:calc_pdf_Export:{\"SinglePageSheets\":{\"type\":\"boolean\",\"value\":\"true\"}}"
    output_dir = os.path.dirname(output_file_path)
    cmd = [
        "soffice",
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--convert-to", convert_to,
        "--outdir", output_dir,
        input_file_path,
    ]
    subprocess.run(cmd, check=True)

    # ファイル名を変更
    output_file_name = os.path.basename(input_file_path).replace(os.path.splitext(input_file_path)[1], ".pdf")
    os.rename(os.path.join(output_dir, output_file_name), output_file_path)
