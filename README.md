# gsapi
A REST API interface written in pyhton with FASTAPI for ghostscript


curl.exe -v http://127.0.0.1:8000/convert -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@0001.pdf" -o o2-1.pdf