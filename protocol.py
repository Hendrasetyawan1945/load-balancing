import json
import socket

BUF_SIZE = 4096

def send_message(sock: socket.socket, data: dict):
    """
    Mengirimkan payload dictionary sebagai string JSON dengan delimiter newline.
    """
    message = json.dumps(data) + "\n"
    sock.sendall(message.encode("utf-8"))

def receive_message(sock: socket.socket) -> dict:
    """
    Menerima pesan stream TCP hingga menemukan delimiter newline '\n',
    lalu mendecode menjadi dictionary.
    """
    buffer = ""
    while True:
        chunk = sock.recv(BUF_SIZE).decode("utf-8")
        if not chunk:
            break
        buffer += chunk
        if "\n" in buffer:
            line, _ = buffer.split("\n", 1)
            return json.loads(line)
    return {}
