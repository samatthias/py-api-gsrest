from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from starlette.background import BackgroundTasks
import shutil
import os
import subprocess

app = FastAPI()

@app.post("/mergepdf")
async def merge_pdf_files(background_tasks : BackgroundTasks, file: UploadFile = File(...)):
  print(f'Content type of file: {file.content_type}')

  # Prepare file for processing
  tmpDir = "/tmp/"
  inputFileName = file.filename
  inputFilePath = tmpDir + inputFileName
  
  # Save uplodaed file
  with open(inputFilePath, "wb") as buffer:
    shutil.copyfileobj(file.file, buffer)

  command = "unzip " + inputFilePath + " -d " + tmpDir
  print(command)
  result = subprocess.run(command, shell=True, capture_output=True, text=True)
  print("Return Code:", result.returncode)
  print("Output:", result.stdout)

  # qpdf --empty --pages *.pdf -- new.pdf

  command = "qpdf --empty --pages /tmp/*.pdf -- /tmp/tmp.pdf"
  print(command)
  result = subprocess.run(command, shell=True, capture_output=True, text=True)
  print("Return Code:", result.returncode)
  print("Output:", result.stdout)

  # cleanup /tmp/ directory
  background_tasks.add_task(remove_file, tmpDir)

  return FileResponse("/tmp/tmp.pdf", media_type="application/pdf", filename="tmp.pdf")



@app.post("/metadata")
async def readbarcode_from_pdf(background_tasks : BackgroundTasks, file: UploadFile = File(...)):
   print(f'Content type of file: {file.content_type}')

   # Prepare file for processing
   tmpDir = "/tmp/"
   inputFileName = file.filename
   inputFilePath = tmpDir + inputFileName

   # Save uplodaed file
   with open(inputFilePath, "wb") as buffer:
     shutil.copyfileobj(file.file, buffer)
   
   # json dict
   return_message = {}
   return_message['fileName'] = inputFileName


   # convert -density 300 -crop 500x500+2050+0 2_AD.pdf jpg:- | zbarimg --nodbus --nodisplay --quiet --raw -
   # convert 0__ADempty.pdf -format '%[mean] %[max]' info:- | awk '{print $1/$2}'
   # convert -density 300 2_AD.pdf jpg:- | identify -ping -format '%w' -
   # convert pdf to jpg

   # read width from jpg in pdf
   command = "convert -density 300 " + inputFilePath + " jpg:- | identify -ping -format '%w' -"
   print(command)
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   print("Return Code:", result.returncode)
   print("Output:", result.stdout)
   return_message['width'] = result.stdout.strip()


   # read percentage of white pixels from jpg in pdf
   command = "convert " + inputFilePath + " -format '%[mean] %[max]' info:- | awk '{print $1/$2}'"
   print(command)
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   print("Return Code:", result.returncode)
   print("Output:", result.stdout)
   return_message['percentageWhitePixels'] = result.stdout.strip()


   # read barcode
   return_message['barcode'] = "NONE"
   calcStartpointX = int(return_message['width']) - 500
   regionOfInterest = "500x500+" + str(calcStartpointX) +"+0"
   # 1) convert -density 300 -crop 500x500+1980+0 0015.pdf jpg:- | zbarimg --nodbus --nodisplay --quiet --raw -
   # 2) convert +repage -define profile:skip=icc -threshold 50% -morphology open square:1 -density 300 -crop 500x500+1980+0 in.pdf out.png
   #
   # -density 300 = resolution of image
   # -crop 500x500+1980+0 = cut a rectangle from the original image width+heigth+start_x+start_y
   # +repage =  Removes virtual canvas metadata Source: https://stackoverflow.com/questions/69689869/improve-zbarimg-qrcode-recognition
   # -define profile:skip=icc = elimininate icc color warning from image magick Source: https://github.com/ImageMagick/ImageMagick/discussions/6292
   # -threshold 50% = convert to binary Source: https://stackoverflow.com/questions/69689869/improve-zbarimg-qrcode-recognition
   #
   # -morphology open square:1 = Cleans small imperfections without altering code structure
   # Source 1: https://github.com/mchehab/zbar/issues/123
   # Source 2: https://stackoverflow.com/questions/69689869/improve-zbarimg-qrcode-recognition

   # zbarimg improvements
   # 1) zbarimg --nodbus --nodisplay --quiet --raw in.jpg
   # 
   # -Sdisable = turns off all decoders
   # Sources: https://kb.offsec.nl/tools/forensics/zbar-tools/
   # http://c3codes.ourproject.org/C3_Codes_Tutorial.pdf

   # -Sqrcode.enable = re-enables only QR codes
   # Sources: https://kb.offsec.nl/tools/forensics/zbar-tools/
   # https://manpages.ubuntu.com/manpages/bionic/man1/zbarimg.1.html
   #
   # Avoid JPG artifacts: Use PNG for intermediate processing to prevent quality loss
   #
   # 


   command = "convert +repage -define profile:skip=icc -threshold 50% -morphology open square:1 -density 300 -crop " + regionOfInterest + " " + inputFilePath + " jpg:- | zbarimg -Sdisable -Sqrcode.enable --nodbus --nodisplay --quiet --raw -"
   print(command)
   result = subprocess.run(command, shell=True, capture_output=True, text=True)
   print("Return Code:", result.returncode)
   print("Output:", result.stdout)
   if (result.stdout.strip()):
    return_message['barcode'] = result.stdout.strip()

    

    # remove file after return the json message
    background_tasks.add_task(remove_file, tmpDir)
   return return_message
   

@app.post("/convertpdfa")
async def convert_pdfa(background_tasks : BackgroundTasks, file: UploadFile = File(...)):
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
    background_tasks.add_task(remove_file, "/tmp/")
    return FileResponse("/tmp/" + outputFileName, media_type="application/pdf", filename=outputFileName)
        


def remove_file(dir: str) -> None:
  for root, dirs, files in os.walk(dir):
    for file in files:
        os.remove(os.path.join(root, file))
    
