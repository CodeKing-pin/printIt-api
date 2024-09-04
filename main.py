from typing import Optional
import json
import sqlite3
import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import paramiko

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5175"],  # Adjust this to your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def sendFileToRpi(filename: str):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect('192.168.195.108', username='pi', password='pi')
        sftp = ssh.open_sftp()

        localpath = f'files/{filename}'
        remotepath = f'Desktop/PrintIt/files/{filename}'
        sftp.put(localpath, remotepath)
        sftp.close()
        ssh.close()
    except Exception as e:
        print(f"Error sending file to RPi: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending file to RPi")

def pageCounter():
    try:
        with open("renamingPages.json", 'r') as f:
            pages = json.load(f).get('pages', {})
        return pages
    except Exception as e:
        print(f"Error reading page counter: {str(e)}")
        raise HTTPException(status_code=500, detail="Error reading page counter")

@app.get("/api/v1/getPrinterDetails")
def get_printer_details():
    try:
        pageCount = pageCounter()
        return {"deviceName": "RCOEM EN PRINTER", "pageCount": pageCount}
    except HTTPException as e:
        raise e

@app.post("/api/v1/uploadFile")
def upload_file(numPages: int = 1, printerName: Optional[str] = None, file: UploadFile = File(...)):
    try:
        # Save file locally
        file_location = f"files/{file.filename}"
        with open(file_location, 'wb') as f:
            f.write(file.file.read())

        # Update database
        con = sqlite3.connect('printJobs.db')
        cur = con.cursor()
        insert_statement = """
        INSERT INTO printJobs (time, numPages, printerName, success)
        VALUES (?, ?, ?, ?)
        """
        cur.execute(insert_statement, (time.time(), numPages, printerName, False))
        con.commit()
        con.close()

        # Send file to RPi (uncomment this line if needed)
        # asyncio.create_task(sendFileToRpi(file.filename))

        return {"message": f"Successfully uploaded {file.filename}"}
    except Exception as e:
        return {"message": f"There was an error uploading the file: {str(e)}"}
    finally:
        file.file.close()
