from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks
import shutil
import os

app = FastAPI()

@app.post("/convert")
async def convert_pdf(background_tasks : BackgroundTasks, file: UploadFile = File(...)):
    # Temporärer Pfad zum Speichern der hochgeladenen Datei
    #temp_file = f"{file.filename}"
    print(f'Content type of file: {file.content_type}')
    
    # Speichern der hochgeladenen Datei
    with open("/tmp/" + file.filename, "wb") as buffer:
       shutil.copyfileobj(file.file, buffer)
    print(file.filename)
       
    # Rückgabe der Datei als Response
    #headers = {'Content-Disposition': 'inline; filename="out.pdf"'}
    background_tasks.add_task(remove_file, "/tmp/" + file.filename)
    return FileResponse("/tmp/" + file.filename, media_type="application/pdf", filename=file.filename)
        


def remove_file(path: str) -> None:
    if os.path.exists(path):
      os.remove(path)
    
    #finally:
    #    # Aufräumen: Löschen der temporären Datei
    #    print("finally")
    #    if os.path.exists("C:/Users/Matthias/Documents/github/tmp/" +file.filename):
    #      os.remove("C:/Users/Matthias/Documents/github/tmp/" +file.filename)
