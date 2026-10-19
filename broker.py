import argparse
import socket
import threading
from protocol import send_message, receive_message

class BrokerServer:
    def __init__(self, host: str, port: int, mode: str = "round_robin"):
        self.host = host
        self.port = port
        self.mode = mode  # 'round_robin' atau 'least_requests'
        
        # Daftar 3 Worker dalam Cluster
        self.workers = [
            {"id": 1, "host": "127.0.0.1", "port": 5001, "requests_served": 0},
            {"id": 2, "host": "127.0.0.1", "port": 5002, "requests_served": 0},
            {"id": 3, "host": "127.0.0.1", "port": 5003, "requests_served": 0},
        ]
        
        self.rr_counter = 0
        self.lock = threading.Lock()

    def select_worker(self) -> dict:
        """
        Memilih salah satu dari 3 worker berdasarkan 2 pendekatan alokasi:
        1. 'least_requests': Pemerataan beban (pilih worker dengan request tersedikit)
        2. 'round_robin'   : Berurutan berdasar counter milik broker
        """
        with self.lock:
            if self.mode == "least_requests":
                # Pendekatan 1: Pemerataan jumlah request yang sudah dilayani
                selected = min(self.workers, key=lambda w: w["requests_served"])
                selected["requests_served"] += 1
                explanation = f"[Pemerataan / Least Requests] Worker #{selected['id']} beban terendah ({selected['requests_served']-1} -> {selected['requests_served']})"
            else:
                # Pendekatan 2: Berurutan sesuai server-id berdasar counter broker
                selected_idx = self.rr_counter % len(self.workers)
                selected = self.workers[selected_idx]
                selected["requests_served"] += 1
                explanation = f"[Round Robin] Counter broker={self.rr_counter} => Worker #{selected['id']}"
                self.rr_counter += 1

            return selected, explanation

    def forward_to_worker(self, worker_info: dict, request_data: dict) -> dict:
        """
        Meneruskan request ke worker via socket TCP dan mengembalikan responsenya.
        """
        worker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        worker_sock.settimeout(10.0)
        try:
            worker_sock.connect((worker_info["host"], worker_info["port"]))
            send_message(worker_sock, request_data)
            response = receive_message(worker_sock)
            return response
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Gagal menghubungi Worker #{worker_info['id']} di {worker_info['port']}: {e}"
            }
        finally:
            worker_sock.close()

    def handle_client(self, client_sock: socket.socket, client_addr):
        try:
            request_data = receive_message(client_sock)
            if not request_data:
                return

            req_id = request_data.get("request_id", "N/A")
            app_id = request_data.get("app_id", "SHORT")
            client_name = request_data.get("client_name", str(client_addr))

            print("\n" + "="*65)
            print(f"[BROKER] Menerima request [{req_id}] dari {client_name} ({client_addr})")
            print(f"         ├─ Application ID : {app_id}")
            print(f"         └─ Payload        : {request_data.get('payload', '')}")

            # Pilih Worker sesuai algoritma
            worker, reason = self.select_worker()
            print(f"[BROKER] Routing Decision : {reason}")
            print(f"         └─ Menuju Worker  : Worker #{worker['id']} ({worker['host']}:{worker['port']})")

            # Tampilkan rekap status cluster
            stats = ", ".join([f"W{w['id']}: {w['requests_served']} req" for w in self.workers])
            print(f"[BROKER] Statistik Cluster: [{stats}]")

            # Teruskan request ke worker
            worker_response = self.forward_to_worker(worker, request_data)

            # Kembalikan response worker ke client
            send_message(client_sock, worker_response)
            print(f"[BROKER] Selesai: Response dari Worker #{worker['id']} dikirim balik ke client.\n" + "="*65)

        except Exception as e:
            print(f"[BROKER] Error memproses client: {e}")
            send_message(client_sock, {"status": "ERROR", "message": str(e)})
        finally:
            client_sock.close()

    def start(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.host, self.port))
        server_sock.listen(20)

        print("*" * 65)
        print(f" [BROKER LOAD BALANCER AKTIF] di {self.host}:{self.port}")
        print(f" Mode Alokasi : {self.mode.upper()}")
        print(f" Cluster      : 3 Worker Servers (Port 5001, 5002, 5003)")
        print("*" * 65 + "\n")

        try:
            while True:
                client_sock, client_addr = server_sock.accept()
                t = threading.Thread(target=self.handle_client, args=(client_sock, client_addr))
                t.daemon = True
                t.start()
        except KeyboardInterrupt:
            print("\n[BROKER] Mematikan broker...")
        finally:
            server_sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Broker Load Balancer Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Broker Host")
    parser.add_argument("--port", type=int, default=5000, help="Broker Port")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["round_robin", "least_requests"],
        default="round_robin",
        help="Pendekatan alokasi: 'round_robin' (berurutan) atau 'least_requests' (pemerataan beban)"
    )
    args = parser.parse_args()

    broker = BrokerServer(host=args.host, port=args.port, mode=args.mode)
    broker.start()
