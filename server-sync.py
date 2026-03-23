import socket
import os

HOST = '127.0.0.1'
PORT = 8888


ADDR = (HOST, PORT)

FILE_DIR = 'server_folder'

BUFF_SIZE = 1024

if not os.path.exists(FILE_DIR): os.makedirs(FILE_DIR)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind(ADDR)
server.listen(5)
print(f"[PALANTIR] listening on {HOST}:{PORT}")

while True:
    connection, address = server.accept()
    print(f"Connected by {address}")
    with connection:
        while True:
            data = connection.recv(BUFF_SIZE)
            if not data: break
            lines = data.decode().split('\n')
            for li in lines:
                if not li: continue
                if li.startswith('/list'):
                    files = os.listdir(FILE_DIR)
                    response = '\n'.join(files) + '\n'
                    connection.sendall(response.encode())
                else: connection.sendall(data)
    print(f"{address} disconnected")
