import httpx
import asyncio
import os
from pathlib import Path
import datetime
import requests
from urllib.request import urlopen
import json

url = "https://srs-ssms.com/check_files_pdf.php"

try:
    # store the response of URL
    response = urlopen(url)
    pdf_files_di_server = json.loads(response.read())
except Exception as e:
    print("An error occurred while fetching the server data:", str(e))
    pdf_files_di_server = []

current_date = datetime.datetime.now()
formatted_date = current_date.strftime('%Y-%m-%d')

folderPDF = Path(os.getcwd() + '/hasil/' + formatted_date)
filenames = []

# print('PDF di server :' + str(pdf_files_di_server))
if folderPDF.exists():
    for file in folderPDF.iterdir():
        if file.is_file() and file.suffix.lower() == '.pdf':
            filenames.append(file)

pdf_lokal = [file.name for file in filenames]

pdf_files_difference = list(set(pdf_lokal) - set(pdf_files_di_server))

# print('List PDF lokal : ' + str(pdf_files_difference))
differing_files = []

if folderPDF.exists():
    for file in folderPDF.iterdir():
        if file.is_file() and file.suffix.lower() == '.pdf' and file.name in pdf_files_difference:
            differing_files.append(file)


async def upload_pdf(pdf_file_path, upload_url):
    try:
        async with httpx.AsyncClient() as client:
            with open(pdf_file_path, 'rb') as pdf_file:
                response = await client.post(upload_url, files={'pdf_file': pdf_file})
            return response
    except Exception as e:
        print(f"An error occurred while uploading {pdf_file_path}: {str(e)}")
        return None


async def main():
    upload_url = "https://srs-ssms.com/pdf_grading/uploadPDFGradingSampling.php"

    if not differing_files:
        print("Tidak ada file yang belum di upload.")
    else:
        for pdf_file in differing_files:
            response = await upload_pdf(pdf_file, upload_url)

            if response is not None:
                if response.status_code == 200:
                    print(f"Upload of {pdf_file} successful!")
                    # print("Response:", response.text)
                else:
                    print(f"Upload of {pdf_file} failed. Status code:", response.status_code)


if __name__ == "__main__":
    asyncio.run(main())