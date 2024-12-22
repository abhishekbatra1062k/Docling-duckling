import json
import logging
import time
from pathlib import Path
import os
from docling.document_converter import DocumentConverter
import pandas as pd
import csv

path = r"/content/Pdf_Files"
converter = DocumentConverter()
output_dir = os.path.join(path, "scratch")
os.makedirs(output_dir, exist_ok=True)

output_csv_path = os.path.join(output_dir, "output.csv")

out_dict = []

for file in os.listdir(path):
  base_filename, ext = os.path.splitext(file)
  if ext.lower() not in [".pdf"]: continue
  
  start_time = time.time()
  
  file_path = os.path.join(path, file)
  conv_result = converter.convert(file_path)
  doc_filename = conv_result.input.file.stem

  time_elapsed = time.time() - start_time

  json_result = conv_result.document.export_to_dict()
  
  with open(os.path.join(output_dir, f"{base_filename}.json"), "w") as fp:
    fp.write(json.dumps(json_result))
  with open(os.path.join(output_dir, f"{base_filename}.html"), "w") as fp:
    fp.write(conv_result.document.export_to_html())
  
  for table_ix, table in enumerate(conv_result.document.tables):
    table_df: pd.DataFrame = table.export_to_dataframe()

    element_csv_filename = os.path.join(output_dir, f"{base_filename}-table-{table_ix+1}.csv")
    table_df.to_csv(element_csv_filename)

  out_dict.append({
      "filename": file,
      "file_size": os.path.getsize(file_path),
      "no_of_pages": len(json_result["pages"].keys()),
      "time": time_elapsed
  })

with open(output_csv_path, mode="w", newline="") as file:
  writer = csv.DictWriter(file, fieldnames=["filename", "no_of_pages", "time"])
  writer.writeheader()
  writer.writerows(out_dict)
print(out_dict)
