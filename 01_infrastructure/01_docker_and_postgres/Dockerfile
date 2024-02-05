# image docker dasar
FROM python:3.9

# install library menggunakan pip
RUN pip install pandas

# mengatur direktori kerja di container
WORKDIR /app

# menyalin skrip ke container, sumber -> tujuan
COPY pipeline.py pipeline.py

# definisikan apa yang akan dilakukan pertama kali ketika container dijalankan
ENTRYPOINT [ "python", "pipeline.py" ]
