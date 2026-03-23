import socket

HOST = '127.0.0.1'
PORT = 8888

ADDR = (HOST, PORT)

BUFF_SIZE = 1024

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
            connection.sendall(data)
    print(f"{address} disconnected")
