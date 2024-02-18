# Data Engineering Zoomcamp 2024

Data Engineering Zoomcamp adalah program belajar Data Engineering yang dipelopori oleh [DataTalks.Club](https://www.youtube.com/@DataTalksClub).

## 1. Pengenalan Docker

- Apa itu docker?

  Docker adalah platform open-source yang digunakan untuk mengembangkan, mengirim, dan menjalankan aplikasi di dalam container. Kontainer Docker memungkinkan pengembang untuk mengemas aplikasi bersama dengan semua dependensinya, termasuk library, runtime environment, dan konfigurasi, sehingga dapat dijalankan di berbagai environment.

- Kenapa perlu docker?

  - Portabilitas: Docker memungkinkan pengemasan aplikasi bersama dengan semua dependensinya ke dalam kontainer yang dapat dijalankan di berbagai environment. Ini membuat aplikasi lebih portabel, memastikan konsistensi antara environment pengembangan, pengujian, dan produksi.
  - Isolasi: Kontainer Docker memberikan isolasi yang kuat di tingkat sistem operasi. Setiap kontainer menjalankan aplikasi dan dependensinya dalam environment terisolasi, yang meminimalkan konflik dan masalah yang mungkin timbul akibat perbedaan konfigurasi atau dependensi.
  - Efisiensi Sumber Daya: Kontainer menggunakan sumber daya lebih efisien dibandingkan dengan mesin virtual tradisional. Mereka dapat memanfaatkan sumber daya dari sistem operasi host dan berbagi kernel dengan host, mengurangi overhead dan memungkinkan penggunaan sumber daya yang lebih efisien.
  - Skalabilitas: Docker memungkinkan untuk dengan mudah menyalakan dan mematikan kontainer, sehingga memungkinkan skalabilitas yang cepat dan efisien. Ini berguna dalam situasi di mana aplikasi perlu menangani beban kerja yang berfluktuasi.
  - Manajemen Dependensi: Docker menyederhanakan manajemen dependensi dan konfigurasi dengan memastikan bahwa semua dependensi dan konfigurasi aplikasi diatur dalam Docker Image. Ini memungkinkan pengembang dan tim operasional untuk dengan mudah mengimplementasikan aplikasi tanpa perlu khawatir tentang konflik versi atau konfigurasi.
  - Pengembangan Kolaboratif: Dengan Docker, tim pengembang dapat bekerja dalam lingkungan yang seragam dan dapat diulang. Setiap anggota tim dapat menjalankan aplikasi dalam kontainer yang identik, mengurangi potensi masalah yang muncul karena perbedaan konfigurasi lokal.
  - Dan lain-lain

- Data Pipeline di Data Engineering

  Data Pipeline adalah seperangkat alat (biasanya berupa script python atau bash) dan proses untuk memindahkan data dari satu sistem ke sistem lainnya di mana ia dapat disimpan dan dikelola secara berbeda. Data pipeline memungkinkan kamu mendapatkan informasi dari banyak sumber yang berbeda kemudian mentransformasikan dan menggabungkannya dalam satu tempat penyimpanan data.

- Instalasi & Testing Docker

  Misal ingin run container pake images ubuntu

  ```bash
  docker run -it ubuntu bash
  ```

  Misal ingin run container pake images python

  ```bash
  docker run -it python
  ```

  Misal ingin run container pake images python dan masuk ke bash

  ```bash
  docker run -it --entrypoint=bash python
  ```

- Test Data Ingestion Sederhana

  Buat file `pipeline.py`, script ini akan menerima argumen dan menampilkannya

  ```bash
  import sys
  import pandas

  print(sys.argv)

  # argumen 0 adalah nama file
  # argumen 1 berisi argumen pertama yang sebenarnya kita perlukan
  day = sys.argv[1]

  print(f'job finished successfully for day {day}')
  ```

  Selanjutnya buat `Dockerfile` di folder yang sama

  ```bash
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
  ```

  Build imagesnya

  ```bash
  docker build -t repository:version .
  ```

  Jalankan kontainernya

  ```bash
  # docker run -it images argumen
  docker run -it test:pandas 2024-01-01
  ```

## 2. Data Ingestion ke Postgres

- Postgres

  - PostgreSQL adalah sebuah object-relational database system open source. Postgres terkenal dengan reliabilitas, fitur dan performanya.

- Instalasi PostgreSQL di Docker

  ```bash
  docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 2345:5432 \
    postgres:13
  ```

  Perintah diatas menjalankan container PostgreSQL versi 13 dengan username "root" dan password "root", membuat database "ny_taxi", menyimpan data pada volume yang dikaitkan dengan host kita dan membuat database tersebut dapat diakses dari port 2345 di host kita.

- Akses database dengan pgcli
  Setelah berhasil run container postgres, kita akan akses menggunakan pgcli (library python untuk akses database postgres).

  Install pgcli

  ```bash
  pip install pgcli
  ```

  Akses postgres dengan pgcli

  ```bash
  pgcli -h localhost -p 2345 -u root -d ny_taxi
  ```

- Install jupyter

  ```bash
  pip install jupyter
  ```

  Setelah terinstall, jalankan jupyter dengan perintah

  ```bash
  jupyter notebook
  ```

- Dataset
  Klik [link ini](https://github.com/DataTalksClub/nyc-tlc-data?tab=readme-ov-file) untuk download datasetnya
  Klik [link ini](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf) untuk tau lebih detail penjelasan dari masing-masing kolom

- Cek isi dataset yellow taxi
  Tampilkan jumlah row

  ```bash
  wc -l nama-file.csv
  ```

  Tampilkan 100 baris paling atas

  ```bash
  head -n 100 nama-dataset.csv
  ```

- Memasukkan data ke postgres
  Kita akan memasukkan data ke postgres pake pandas & jupyter notebook. Berikut langkah-langkahnya:

  - Import pandas dan buat koneksi ke database dengan library `sqlalchemy`

    ```bash
    import pandas as pd
    from sqlalchemy import create_engine

    # format url : 'postgresql://[user]:[password]@[host]:[port]/[dbname]'
    engine = create_engine('postgresql://root:root@localhost:2345/ny_taxi')
    ```

  - Masukkan data pakai chunk, karena datanya lumayan banyak, ada lebih dari 1 juta data

    ```bash
    # Membagi data dalam chunk
    df_iter = pd.read_csv('yellow_tripdata_2021-01.csv', iterator=True, chunksize=100000)

    # dapatkan chunk pertama dan simpan ke variabel df
    df=next(df_iter)
    ```

  - Buat tabel di db dengan memanfaatkan header dari data kita. Caranya dengan membuat dataframe yang hanya ada data kolomnya.

    ```bash
    # head(n=0), ambil data paling atas (kalo scv biasanya nama-nama kolom)
    df.head(n=0).to_sql(name='yellow_tripdata_2021_01', con=engine, if_exists='replace')
    ```

  - Masukkan semua data pake fungsi iterasi di Python

    ```bash
    # impor modul time untuk tracking waktu
    from time import time

    #loop akan berjalan sampai terjadi exception seperti StopIteration
    while True:
      t_start = time()
      df = next(df_iter) # mengambil next chunk dari df_iter

      # ubah kolom tpep_pickup_datetime dan tpep_dropoff_datetime (string -> datetime) pake pandas.to_datetime
      df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
      df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

      # simpan dataframe ke tabel yellow_taxi_data
      df.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')

      t_end = time()

      print('inserted another chunk, took %.3f second' % (t_end - t_start))
    ```

## 3. Menghubungkan pgAdmin dan Postgres

- setup pgAdmin dengan docker
  https://hub.docker.com/r/dpage/pgadmin4/

  - buat docker network

    ```bash
    docker network create pg-network
    ```

  - jalankan container postgres dengan network `pg-network`

    ```bash
    docker run -it \
      -e POSTGRES_USER="root" \
      -e POSTGRES_PASSWORD="root" \
      -e POSTGRES_DB="ny_taxi" \
      -v ny_taxi_postgres_data:/var/lib/postgresql/data \
      -p 2345:5432 \
      --network=pg-network \
      --name=pgdatabase \
      postgres:13
    ```

  - jalankan container pgAdmin dengan network `pg-network`

    ```bash
    docker run -it \
      -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
      -e PGADMIN_DEFAULT_PASSWORD="root" \
      -p 8080:80 \
      --network=pg-network \
      --name=pgadmin \
      dpage/pgadmin4
    ```

    - `docker run -it` : untuk menjalankan kontainer docker. Opsi `-it` untuk mengaktifkan mode interaktif dengan TTY yang terhubung, memungkinkan kita berinteraksi dengan container melalui terminal.
    - `-e PGADMIN_DEFAULT_EMAIL="admin@admin.com"` : ini menetapkan environment variabel `PGADMIN_DEFAULT_EMAIL` di dalam container. Ini akan menjadi email default untuk masuk ke pgAdmin.
    - `-e PGADMIN_DEFAULT_PASSWORD="root"` : ini menetapkan environment variabel `PGADMIN_DEFAULT_PASSWORD` di dalam container. Ini akan menjadi password default yang digunakan untuk masuk ke pgAdmin.
    - `-p 8080:80` : untuk mengatur port forwarding dari container ke host. `8080` itu port di host, `80` itu port containernya. Itu artinya, kita dapat mengakses pgAdmin yang ada di dalam container melalui port `8080`.
    - `dpage/pgadmin4` : ini adalah nama repository dan imagenya.

  - akses pgAdmin di browser `http://localhost:8080`
  - tambahkan koneksi ke postgres
    - host : `nama_container`
    - port : `5432`
    - username : `root`
    - password : `root`

## 4. Dockerizing data ingestion

- convert jupyter notebook ke python script
  ```bash
  jupyter nbconvert --to=script upload-data.ipynb
  ```
- bersihkan kodenya
- rename jadi `ingest_data.py`
- konfigurasi argumen pakai `argparse`
- wrap kode ke fungsi `main()`
- unpacking parameter dari argument yang sudah dibuat
- implementasi parameter ke kode
- membuat main block di python
  - parse argument
  - jalankan fungsi `main()`
- jalankan scriptnya
  ```bash
  URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
  python ingest_data.py \
    --user=root \
    --password=root \
    --host=localhost \
    --port=2345 \
    --dbname=ny_taxi \
    --table=yellow_taxi_trip \
    --url=${URL}
  ```

## 5. Dockerizing ingestion script

- buat dockerfile untuk membuat image yang berisi ingestion pipeline

  ```bash
  # image docker dasar
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
  ```

- bikin docker image dari dockerfile

  ```bash
  docker build -t taxi_ingest:v1.0 .
  ```

- jalankan container menggunakan image yang telah dibuat
  ```bash
  docker run -it \
    --network=pg-network \
    taxi_ingest:v1.0 \
      --user=root \
      --password=root \
      --host=pgdatabase \
      --port=5432 \
      --dbname=ny_taxi \
      --table=yellow_taxi_trips \
      --url=${URL}
  ```

## 6. Menjalankan Postgres dan pgAdmin dengan Docker Compose

- Docker Compose
  Tools untuk membantu kita mendefinisikan dan menjalankan multi container Docker. Dengan Docker Compose kita bisa mendefinisikan semua container kita dalam satu file dan menyiapkan semua service yang kita butuhkan.
- Setup Docker Compose
  Buat file `docker-compose.yml`, isi dengan script berikut :
  ```bash
  services:
  # konfigurasi postgres
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
    ports:
      - "2345:5432"
  # konfigurasi pgAdmin
  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8080:80"
  ```
- jalankan docker compose `docker compose up`

## 7. Terraform

- Apa itu Terraform
  [Terraform](https://terraform.io/) adalah alat open-source yang digunakan untuk mengelola infrastruktur sebagai kode (Infrastructure as Code atau IaC). Dengan Terraform, Anda dapat mendefinisikan dan menyusun infrastruktur teknologi, seperti mesin virtual, jaringan, dan sumber daya cloud, menggunakan sintaks berbasis konfigurasi.

  Istilah "infrastruktur sebagai kode" berarti Anda dapat mendeskripsikan semua elemen infrastruktur yang dibutuhkan untuk aplikasi atau proyek Anda dalam berkas konfigurasi yang dapat dibaca oleh manusia. Setelah konfigurasi tersebut diatur, Terraform dapat mengeksekusi perubahan pada infrastruktur dengan otomatis, memastikan keberlanjutan dan konsistensi dalam pengelolaan infrastruktur.

  Terraform mendukung berbagai penyedia cloud, seperti AWS, Google Cloud, Microsoft Azure, dan lainnya. Dengan menggunakan Terraform, tim pengembangan dan operasional dapat bekerja sama secara efisien untuk menyusun, menyelaraskan, dan memelihara infrastruktur dengan cara yang terstruktur dan dapat dipantau.

  ![Konsep Terraform](https://spaceliftio.wpcomstaging.com/wp-content/uploads/2023/03/terraform-architecture-diagram.png)

  - Terraform manifest : kode Terraform yang kita siapkan untuk mendefinisikan Terraform.
  - Providers : Code API yang memungkinkan Terraform untuk dapat berkomunikasi dan memanage resources dari berbagai services.
  - Cloud Services : Service di cloud yang akan di manage oleh Terraform.

- Perintah Utama
  - `terraform init` : Menyiapkan semua kebutuhan
  - `terraform plan` : Apa saja yang mau dilakukan
  - `terraform apply` : Implementasi
  - `terraform destroy` : Hapus semua yang sudah dibuat
