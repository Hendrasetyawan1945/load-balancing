import argparse
import socket
import threading
import time
from protocol import send_message, receive_message

class WorkerServer:
    def __init__(self, worker_id: int, host: str, port: int):
        self.worker_id = worker_id
        self.host = host
        self.port = port
        self.total_served = 0
        self.lock = threading.Lock()

    def process_application(self, app_id: str, payload: str):
        """
        Memproses request berdasarkan Application ID:
        1. SHORT: Echo atau perhitungan sederhana (cepat)
        2. LONG: Perhitungan kompleks (simulasi komputasi intensif)
        """
        start_time = time.time()
        app_id_upper = app_id.upper()

        if app_id_upper == "SHORT":
            # Perhitungan sederhana / Echo
            result = f"ECHO: '{payload}' | Panjang: {len(payload)} karakter"
            time.sleep(0.05)  # Latensi mikro normal
        elif app_id_upper == "LONG":
            # Simulasi komputasi kompleks (misal kalkulasi faktorial & pemrosesan)
            total_sum = sum(i * i for i in range(100000))
            time.sleep(1.2)   # Simulasi durasi pemrosesan komputasi berat
            result = f"KOMPUTASI BERAT SELESAI [Checksum: {total_sum}] untuk data '{payload}'"
        else:
            result = f"UNKNOWN APP_ID '{app_id}'. Default echo: {payload}"

        duration = round(time.time() - start_time, 4)
        return result, duration

    def handle_client(self, client_sock: socket.socket, client_addr):
        try:
            req = receive_message(client_sock)
            if not req:
                return

            req_id = req.get("request_id", "UNKNOWN")
            app_id = req.get("app_id", "SHORT")
            payload = req.get("payload", "")

            with self.lock:
                self.total_served += 1
                curr_count = self.total_served

            print(f"[WORKER #{self.worker_id} : {self.port}] >>> Menerima [{req_id}] dari Broker {client_addr}")
            print(f"   ├─ Jenis Layanan (App ID) : {app_id}")
            print(f"   ├─ Payload                 : {payload}")
            print(f"   └─ Total Dilayani Worker   : {curr_count} request")

            # Eksekusi jenis aplikasi
            result_text, duration = self.process_application(app_id, payload)

            response = {
                "status": "SUCCESS",
                "request_id": req_id,
                "worker_id": self.worker_id,
                "worker_port": self.port,
                "app_id": app_id,
                "result": result_text,
                "execution_time_sec": duration,
                "total_served_by_worker": curr_count
            }

            send_message(client_sock, response)
            print(f"[WORKER #{self.worker_id}] <<< [{req_id}] Selesai dalam {duration}s. Response terkirim kembali ke Broker.\n")

        except Exception as e:
            print(f"[WORKER #{self.worker_id}] Error menangani request: {e}")
        finally:
            client_sock.close()

    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(10)
        print(f"============================================================")
        print(f" [SIAP] Worker #{self.worker_id} aktif di {self.host}:{self.port}")
        print(f"        Mendukung App ID: 'SHORT' (Ringan) & 'LONG' (Kompleks)")
        print(f"============================================================\n")

        try:
            while True:
                client_sock, client_addr = server_sock.accept()
                t = threading.Thread(target=self.handle_client, args=(client_sock, client_addr))
                t.daemon = True
                t.start()
        except KeyboardInterrupt:
            print(f"\n[WORKER #{self.worker_id}] Mematikan server worker...")
        finally:
            server_sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Worker Server Socket")
    parser.add_argument("--id", type=int, required=True, help="Worker ID (1, 2, atau 3)")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Worker Host")
    parser.add_argument("--port", type=int, required=True, help="Worker Port (misal 5001, 5002, 5003)")
    args = parser.parse_args()

    worker = WorkerServer(worker_id=args.id, host=args.host, port=args.port)
    worker.start()
