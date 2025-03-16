from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks
import shutil
import os
import subprocess

app = FastAPI()

@app.post("/convert")
async def convert_pdf(background_tasks : BackgroundTasks, file: UploadFile = File(...)):
    # Temporärer Pfad zum Speichern der hochgeladenen Datei
    #temp_file = f"{file.filename}"
    print(f'Content type of file: {file.content_type}')
    inputFileName = file.filename
    outputFileName = "pdfa_" + file.filename
    print("Input file name:" + inputFileName)
    print("Output file name: " + outputFileName)
    
    # Speichern der hochgeladenen Datei
    with open("/tmp/" + inputFileName, "wb") as buffer:
       shutil.copyfileobj(file.file, buffer)

    command = "gs " 
    command += "-dPDFA " 
    command += "-dBATCH "
    command += "-dNOPAUSE "
    command += "-sColorConversionStrategy=UseDeviceIndependentColor "
    command += "-sDEVICE=pdfwrite "
    command += "-dPDFACompatibilityPolicy=2 "
    command += "-sOutputFile=/tmp/" + outputFileName + " "
    command += "/tmp/" + inputFileName

    print("Ghostsciprt command: " + command)

    subprocess.run(command, shell=True)
       
    # Rückgabe der Datei als Response
    #headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    background_tasks.add_task(remove_file, "/tmp/" + inputFileName)
    background_tasks.add_task(remove_file, "/tmp/" + outputFileName)
    return FileResponse("/tmp/" + outputFileName, media_type="application/pdf", filename=outputFileName)
        


def remove_file(path: str) -> None:
    if os.path.exists(path):
      os.remove(path)
    
    #finally:
    #    # Aufräumen: Löschen der temporären Datei
    #    print("finally")
    #    if os.path.exists("C:/Users/Matthias/Documents/github/tmp/" +file.filename):
    #      os.remove("C:/Users/Matthias/Documents/github/tmp/" +file.filename)
