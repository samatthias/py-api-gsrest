from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import os

app = FastAPI()

@app.post("/convert")
async def convert_pdf(file: UploadFile = File(...)):
    # Temporärer Pfad zum Speichern der hochgeladenen Datei
    temp_file = f"temp_{file.filename}"
    
    try:
        # Speichern der hochgeladenen Datei
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Rückgabe der Datei als Response
        return FileResponse(temp_file, media_type="application/pdf", filename=file.filename)
    
    finally:
        # Aufräumen: Löschen der temporären Datei
        if os.path.exists(temp_file):
            os.remove(temp_file)
