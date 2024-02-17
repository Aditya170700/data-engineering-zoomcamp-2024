FROM python:3.9

# install library menggunakan pip
RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

# mengatur direktori kerja di container
WORKDIR /app

# menyalin skrip ke container, sumber -> tujuan
COPY ingest_data.py ingest_data.py

# definisikan apa yang akan dilakukan pertama kali ketika container dijalankan
ENTRYPOINT [ "python", "ingest_data.py" ]