import subprocess
import time
import sys
from client import send_request

def run_simulation():
    print("="*70)
    print("  SIMULASI LENGKAP LOAD BALANCING SOCKET PYTHON (AKSO / UNESA 2024)")
    print("="*70)

    # 1. Jalankan 3 Worker Server di background
    print("\n[STEP 1] Menyalakan 3 Worker Server (Port 5001, 5002, 5003)...")
    workers = []
    for wid, port in [(1, 5001), (2, 5002), (3, 5003)]:
        p = subprocess.Popen([sys.executable, "worker.py", "--id", str(wid), "--port", str(port)])
        workers.append(p)
    time.sleep(1.0)
    print(">>> 3 Worker Server berhasil aktif.")

    try:
        # =====================================================================
        # SIMULASI 1: Pendekatan 2 - Berurutan sesuai counter broker (Round Robin)
        # =====================================================================
        print("\n" + "#"*70)
        print("  DEMO PENDEKATAN 2: BERURUTAN / ROUND ROBIN (Berdasar Counter Broker)")
        print("#"*70)
        broker_rr = subprocess.Popen([sys.executable, "broker.py", "--port", "5000", "--mode", "round_robin"])
        time.sleep(1.0)

        # Kirim 6 request berurutan
        test_requests = [
            ("REQ-RR-1", "SHORT", "Hitung data A"),
            ("REQ-RR-2", "LONG",  "Simulasi Matriks Kompleks B"),
            ("REQ-RR-3", "SHORT", "Echo teks C"),
            ("REQ-RR-4", "SHORT", "Hitung data D"),
            ("REQ-RR-5", "LONG",  "Simulasi Faktorial Kompleks E"),
            ("REQ-RR-6", "SHORT", "Echo teks F"),
        ]

        for req_id, app_id, payload in test_requests:
            send_request("127.0.0.1", 5000, req_id, app_id, payload, client_name="Tester-RoundRobin")
            time.sleep(0.4)

        broker_rr.terminate()
        broker_rr.wait()
        print("\n>>> Demonstrasi Round Robin Selesai. Broker dimatikan.\n")
        time.sleep(1.0)

        # =====================================================================
        # SIMULASI 2: Pendekatan 1 - Pemerataan jumlah request (Least Requests)
        # =====================================================================
        print("\n" + "#"*70)
        print("  DEMO PENDEKATAN 1: PEMERATAAN BEBAN (Least Requests Served)")
        print("#"*70)
        broker_lr = subprocess.Popen([sys.executable, "broker.py", "--port", "5000", "--mode", "least_requests"])
        time.sleep(1.0)

        test_requests_lr = [
            ("REQ-LR-1", "LONG",  "Komputasi Berat Batch 1"),
            ("REQ-LR-2", "SHORT", "Echo Ringan Batch 1"),
            ("REQ-LR-3", "LONG",  "Komputasi Berat Batch 2"),
            ("REQ-LR-4", "SHORT", "Echo Ringan Batch 2"),
            ("REQ-LR-5", "SHORT", "Echo Ringan Batch 3"),
            ("REQ-LR-6", "LONG",  "Komputasi Berat Batch 3"),
        ]

        for req_id, app_id, payload in test_requests_lr:
            send_request("127.0.0.1", 5000, req_id, app_id, payload, client_name="Tester-LeastRequests")
            time.sleep(0.4)

        broker_lr.terminate()
        broker_lr.wait()
        print("\n>>> Demonstrasi Pemerataan Beban Selesai. Broker dimatikan.\n")

    finally:
        print("\n[CLEANUP] Mematikan seluruh Worker Server...")
        for p in workers:
            p.terminate()
            p.wait()
        print(">>> Seluruh Worker Server berhasil dihentikan. Simulasi selesai!")

if __name__ == "__main__":
    run_simulation()
