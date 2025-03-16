# gsapi
A REST API interface written in pyhton with FASTAPI for ghostscript. It can convert only PDF/A-1b compliant PDFs.

Validator used:
https://demo.verapdf.org/
https://www.pdf-online.com/osa/validate.aspx (End of Service announced in Jun 2024 for end of year 2025)


# test call with curl against python fastapi
curl.exe -v http://127.0.0.1:8080/convert -H "accept: application/json" -H "Content-Type: multipart/form-data" -F "file=@0001.pdf" -o o2-1.pdf

# build in root directory with docker/podman
podman build -t gsapi:v4 -f .\build\Dockerfile .

# run container
podman run -p 8080:8080 -d gsapi:v4

# show logs std out
podman logs <containerid>