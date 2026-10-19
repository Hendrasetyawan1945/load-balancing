import argparse
import socket
import time
from protocol import send_message, receive_message

def send_request(broker_host: str, broker_port: int, req_id: str, app_id: str, payload: str, client_name: str = "Client-App"):
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect((broker_host, broker_port))
        
        request_data = {
            "request_id": req_id,
            "app_id": app_id,
            "payload": payload,
            "client_name": client_name,
            "timestamp": time.time()
        }
        
        print(f"\n[CLIENT] Mengirim [{req_id}] -> Broker ({broker_host}:{broker_port})")
        print(f"         App ID : {app_id} | Payload : '{payload}'")
        
        start_time = time.time()
        send_message(client_sock, request_data)
        
        response = receive_message(client_sock)
        total_rtt = round(time.time() - start_time, 4)
        
        print(f"[CLIENT] Menerima Response untuk [{req_id}]:")
        print(f"         ├─ Status        : {response.get('status')}")
        print(f"         ├─ Dilayani oleh : Worker #{response.get('worker_id')} (Port {response.get('worker_port')})")
        print(f"         ├─ Hasil         : {response.get('result')}")
        print(f"         ├─ Waktu Proses  : {response.get('execution_time_sec')} detik")
        print(f"         └─ Total RTT     : {total_rtt} detik")
        return response
    except Exception as e:
        print(f"[CLIENT] Error: {e}")
        return None
    finally:
        client_sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client Socket Simulator")
    parser.add_argument("--broker-host", type=str, default="127.0.0.1", help="Broker Host")
    parser.add_argument("--broker-port", type=int, default=5000, help="Broker Port")
    parser.add_argument("--app-id", type=str, choices=["SHORT", "LONG"], default="SHORT", help="Application ID")
    parser.add_argument("--payload", type=str, default="Halo dari Client!", help="Pesan request")
    parser.add_argument("--count", type=int, default=1, help="Jumlah request yang dikirim")
    args = parser.parse_args()

    for i in range(1, args.count + 1):
        req_id = f"REQ-{i:03d}"
        send_request(
            broker_host=args.broker_host,
            broker_port=args.broker_port,
            req_id=req_id,
            app_id=args.app_id,
            payload=f"{args.payload} (Iterasi ke-{i})",
            client_name="Client-Terminal"
        )
        if args.count > 1 and i < args.count:
            time.sleep(0.3)
