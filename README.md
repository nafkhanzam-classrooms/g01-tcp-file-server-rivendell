[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/mRmkZGKe)
# Network Programming - Assignment G01

## Anggota Kelompok
| Nama           | NRP        | Kelas     |
| ---            | ---        | ----------|
| Justin Valentino | 5025241234 | C   |
|  Farrel Jatmiko Aji | 5025241193  | C  |

## Link Youtube (Unlisted)
Link ditaruh di bawah ini
```

```

## Penjelasan Program

Project ini adalah implementasi aplikasi client-server berbasis TCP socket.
Fitur utamanya mencakup:

- koneksi multi-client,
- transfer file (upload dan download),
- melihat daftar file di server,
- serta echo message untuk komunikasi dasar.

Yang kami eksplorasi di tugas ini bukan hanya fiturnya, tapi juga cara server menangani banyak client (concurrency). Karena itu, ada 4 versi server dengan pendekatan yang berbeda:

```
server-sync.py   -> sequential (satu client per waktu)
server-thread.py -> multithreading
server-select.py -> I/O multiplexing dengan select
server-poll.py   -> I/O multiplexing dengan poll
```

Satu file client (`client.py`) bisa dipakai untuk berinteraksi dengan semua versi server tersebut.

### Cara Kerja Sistem

Alur komunikasinya sederhana:

1. Client membuka koneksi TCP ke server.
2. Client mengirim command (contoh: `/list`, `/upload`, `/download`).
3. Server membaca request.
4. Server memproses command sesuai logika.
5. Server mengirim response ke client.

Semua data dikirim lewat byte stream TCP dengan buffer 1024 byte.

### Format Komunikasi

Secara umum, data dikirim dalam dua tahap:

1. Header command (teks), format: `[COMMAND ARGUMENT]`
2. Data biner (jika dibutuhkan), misalnya isi file saat upload/download

Contoh header upload:

```
/upload file.txt 100
```

Server akan mem-parsing nama file dan ukuran file, lalu menerima data file sesuai ukuran tersebut.

### Fitur Utama

#### 1) `/list` - Melihat daftar file di server

Client mengirim:

```
/list
```

Server membaca isi folder `server_folder`, lalu mengirimkan daftar file ke client.

#### 2) `/upload` - Mengirim file ke server

Client mengirim header:

```
/upload <filename> <filesize>
```

Setelah itu, client mengirim isi file dalam bentuk biner.

Di sisi server:

- ukuran file dibaca dari header,
- data diterima bertahap sampai ukuran terpenuhi,
- file disimpan ke `server_folder`.

Contoh pola loop penerimaan:

```python
while received < file_size:
    chunk = recv(...)
```

Pola ini memastikan data diterima lengkap sesuai ukuran file.

#### 3) `/download` - Mengambil file dari server

Client request:

```
/download <filename>
```

Jika file ada, server mengirim header:

```
/incoming <filename> <filesize>
```

Lalu server mengirim isi file.

Client kemudian:

- mem-parsing header,
- menerima data file,
- menyimpannya ke local storage.

Catatan: client memakai fungsi `unique()` agar nama file hasil download tidak menimpa file yang sudah ada.

#### 4) Echo message

Jika command tidak dikenali, server akan mengembalikan pesan echo.

Contoh:

```
hello
```

Response:

```
[Lord Elrond Echo]: hello
```

### Perbedaan Implementasi Server

#### 1) `server-sync.py` (Synchronous)

Server melayani satu client dalam satu waktu.

```
accept -> handle -> selesai -> accept berikutnya
```

- Kelebihan: sederhana.
- Kekurangan: client lain harus menunggu.

#### 2) `server-thread.py` (Multithreading)

Setiap client ditangani oleh thread terpisah.

```
accept -> buat thread -> thread handle client
```

Keuntungan: beberapa client bisa dilayani paralel.

#### 3) `server-select.py` (Select)

Menggunakan `select()` untuk memantau banyak socket dalam satu thread.

```
select(list_socket) -> cek socket yang ready
```

Keuntungan: tetap single-thread tetapi mampu menangani banyak koneksi.

#### 4) `server-poll.py` (Poll)

Mirip pendekatan `select`, namun umumnya lebih scalable untuk jumlah socket yang lebih banyak.

### Struktur Folder

```
.
├── client.py
├── server-sync.py
├── server-thread.py
├── server-select.py
├── server-poll.py
└── server_folder/
```

### Cara Menjalankan

1. Jalankan salah satu server:

```bash
python server-sync.py
python server-thread.py
python server-select.py
python server-poll.py
```

2. Jalankan client:

```bash
python client.py
```

3. Gunakan command dari client:

```text
/list
/upload path/to/file.txt
/download file.txt
```

## Screenshot Hasil

Testing dengan `server-sync.py`, gagal ketika client lain mencoba untuk mengakses server (`/list`)
<img width="1538" height="268" alt="image" src="https://github.com/user-attachments/assets/b5b9fb91-1184-4125-9b1a-acd4e1d21fc5" />

Testing dengan `server-thread.py`, kedua client (1 & 2), berhasil mengakses server secara bersamaan.
<img width="1522" height="370" alt="image" src="https://github.com/user-attachments/assets/af44b8b0-40ab-4fec-9c53-20b6904790f9" />

Testing dengan `server-select.py`
<img width="1536" height="374" alt="image" src="https://github.com/user-attachments/assets/c9744200-09cc-4ab2-a90e-525b5bfc2ac5" />

Testing dengan `server-poll.py`
<img width="1544" height="380" alt="image" src="https://github.com/user-attachments/assets/fa688c28-fb44-449d-a33f-5e47291f10a5" />


