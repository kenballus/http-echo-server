"""HTTP echo server. Receives TCP data, sends back an HTTP response containing that data in its message body."""

import socket
import sys
import time

RECV_SIZE = 65536
SOCKET_TIMEOUT = 0.1


def really_recv(sock: socket.socket) -> bytes:
    """Receives bytes from a socket until a timeout expires."""
    result: bytes = b""
    try:
        while b := sock.recv(RECV_SIZE):
            result += b
    except (TimeoutError, ConnectionResetError):
        pass
    return result


def main() -> None:
    """Serve"""
    server_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(("0.0.0.0", 80))
    server_sock.listen()
    while True:
        client_sock, client_address = server_sock.accept()
        print(f"[{time.asctime()}] Got a connection from {client_address}", file=sys.stderr, flush=True)
        client_sock.settimeout(SOCKET_TIMEOUT)
        while payload := really_recv(client_sock):
            print(f"[{time.asctime()}] Received payload: {payload!r}", file=sys.stderr, flush=True)
            try:
                client_sock.sendall(
                        f"HTTP/1.1 200 OK\r\nCache-Control: public, max-age=2592000\r\nServer: echo-python\r\nContent-Length: {len(payload)}\r\n\r\n".encode("ascii") + payload
                )
            except ConnectionResetError:
                print("Connection was reset before I could respond!",file=sys.stderr, flush=True)
        client_sock.close()


if __name__ == "__main__":
    main()
