# Load Balancing Socket Simulation (Python)

Tugas

Buatlah implementasi client-server socket yang mensimulasikan "load balancing" secara sederhana dalam Python. Detail simulasi adalah sebagai berikut:

1. Server utama (broker) menerima request dari client dan mendistribusikan ke 3 server lain (worker) dalam "cluster".
2. Terdapat 2 pendekatan alokasi:
   1. Pemerataan jumlah request yang sudah dilayani oleh masing-masing server pekerja (least_requests).
   2. Berurutan sesuai dengan server-id berdasar counter milik broker (round_robin).
3. Masing-masing worker server mempunyai 2 jenis aplikasi yang dilayani (bisa dimisalkan saja):
   1. `LONG` ⇒ perhitungan yang kompleks (simulasi komputasi berat).
   2. `SHORT` ⇒ echo atau perhitungan sederhana (cepat).
4. Client mengirim pesan request ke broker dengan menyebutkan Application ID. Silakan definisikan sintaks/protokol/messaging format (lihat bagian "Protokol").
5. Broker dan worker mencetak pesan informasi ke layar untuk keperluan debugging/monitoring.

Berkas yang termasuk di repo

- `protocol.py`  — utilitas pengiriman/terima pesan JSON (newline-delimited)
- `client.py`    — fungsi dan CLI untuk mengirim request ke broker
- `broker.py`    — server utama (load balancer) yang memilih worker dan meneruskan request
- `worker.py`    — server pekerja yang memproses request (SHORT / LONG)
- `simulate.py`  — skrip yang menjalankan simulasi lengkap (menyalakan workers, broker, dan mengirim contoh request)

Protokol / Format Pesan

Semua pesan dikirim sebagai JSON dan diakhiri dengan delimiter newline (`\n`). Format pesan request dari client ke broker:

```json
{
  "request_id": "REQ-001",
  "app_id": "SHORT",        // atau "LONG"
  "payload": "Isi data atau perintah",
  "client_name": "Client-Terminal",
  "timestamp": 1670000000.0
}
```

Format response dari worker (yang diteruskan broker ke client):

```json
{
  "status": "SUCCESS",
  "request_id": "REQ-001",
  "worker_id": 2,
  "worker_port": 5002,
  "app_id": "SHORT",
  "result": "Hasil pemrosesan...",
  "execution_time_sec": 0.05,
  "total_served_by_worker": 5
}
```

Cara Menjalankan (Lokal)

1. Clone repo:

   git clone https://github.com/Hendrasetyawan1945/load-balancing.git
   cd load-balancing

2. Menjalankan simulasi lengkap (otomatis menyalakan worker & broker dan mengirim request contoh):

   python simulate.py

3. Menjalankan komponen secara manual:

   - Jalankan 3 worker di terminal terpisah:
     - python worker.py --id 1 --port 5001
     - python worker.py --id 2 --port 5002
     - python worker.py --id 3 --port 5003

   - Jalankan broker (mode `round_robin` atau `least_requests`):
     - python broker.py --port 5000 --mode round_robin

   - Kirim request dari client:
     - python client.py --broker-port 5000 --app-id SHORT --payload "Halo" --count 1

Catatan dan Rekomendasi

- Protokol sederhana diimplementasikan pada berkas `protocol.py`: JSON newline-delimited. Ini mempermudah parsing stream TCP tanpa framing binary.
- Saat menjalankan di Windows/Unix, gunakan `python` atau `python3` sesuai environment Anda.
- Saya dapat menambahkan README lebih rinci, contoh output, atau file `.gitignore`/`LICENSE` jika Anda mau.

Lisensi

Tambahkan lisensi jika diperlukan (mis. MIT) — beri tahu saya jika Anda ingin saya menambahkan berkas `LICENSE`.
