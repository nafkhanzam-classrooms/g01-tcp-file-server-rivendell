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
                
                # LIST FEATURE
                if li.startswith('/list'):
                    files = os.listdir(FILE_DIR)
                    response = '\n'.join(files) + '\n'
                    connection.sendall(response.encode())

                # UPLOAD FEATURE
                elif li.startswith('/upload'):
                    try:
                        parts = li.split()
                        filename = parts[1]
                        file_size = int(parts[2])
                        
                        filepath = os.path.join(FILE_DIR, filename)
                        print(f"[Server] Preparing vault for {filename} ({file_size} bytes)")

                        received = 0
                        with open(filepath, 'wb') as f:
                            while received < file_size:
                                chunk = connection.recv(min(BUFF_SIZE, file_size - received))
                                if not chunk: break
                                f.write(chunk)
                                received += len(chunk)
                        
                        connection.sendall(f"UPLOAD OK: {filename} secured.\n".encode())
                    
                    except IndexError:
                        print("Even the wise must name their burden. Usage: /upload <filename>")

                else: connection.sendall(data)
    print(f"{address} disconnected")
