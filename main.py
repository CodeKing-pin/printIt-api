from typing import Union
import json,sqlite3,time
from fastapi import FastAPI,UploadFile,File
import asyncio
app = FastAPI()
import paramiko

def sendFileToRpi(filename:str):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('192.168.195.108', username='pi', password='pi')
    sftp = ssh.open_sftp()
    
    localpath='files/'+filename
    remotepath='Desktop/PrintIt/files/'+filename
    sftp.put(localpath,remotepath)
    sftp.close()
    ssh.close()
def pageCounter():
    with open("renamingPages.json",'r') as f:
        pages=json.load(f)['pages']
    return pages

@app.get("/api/v1/getPrinterDetails")
def read_root():
    pageCount=pageCounter()
    return {"deviceName": "RCOEM EN PRINTER",
            "pageCount":pageCount}


@app.post("/api/v1/uploadFile")

def upload(numPages :int=1,printerName:str=None,file: UploadFile = File(...)):
    # Checks for proper Input:
    try:
        contents = file.file.read()
        with open("files/"+file.filename, 'wb') as f:
            f.write(contents)
    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
    con=sqlite3.connect('printJobs.db')
    cur=con.cursor()
    insertStatement=f"INSERT INTO printJobs (time,numPages,printerName,success) VALUES(?,?,?,?)"
    cur.execute(insertStatement,(time.time(),numPages,printerName,False))
    con.commit()
    con.close()
    # asyncio.create_task(sendFileToRpi(file.filename))
    return {"message": f"Successfully uploaded {file.filename}"}


