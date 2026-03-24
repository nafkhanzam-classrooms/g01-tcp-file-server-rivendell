import socket
import select
import os

HOST = '127.0.0.1'
PORT = 8888
ADDR = (HOST, PORT)
FILE_DIR = 'server_folder'
BUFF_SIZE = 1024

if not os.path.exists(FILE_DIR): os.makedirs(FILE_DIR)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ADDR)
    server.listen(5)
    print(f"Lord Elrond watches the Palantiri on [{HOST}:{PORT}]")

    inputs = [server]

    while True:
        read, write, execute = select.select(inputs, [], [])

        for sock in read:
            if sock is server:
                connection, address = server.accept()
                inputs.append(connection)
            else:
                try:
                    data = sock.recv(BUFF_SIZE)

                    if not data:
                        print(f"Emissary {sock.getpeername()} gracefully departed.")
                        inputs.remove(sock)
                        sock.close()
                        continue

                    li = data.decode(errors='ignore').strip()
                    if not li: continue
                    
                    # LIST FEATURE
                    if li.startswith('/list'):
                        files = os.listdir(FILE_DIR)
                        response = "Archives:\n" + "\n".join(files) + "\n"
                        sock.sendall(response.encode())

                    # UPLOAD FEATURE
                    elif li.startswith('/upload'):
                        try:
                            parts = li.split()
                            if len(parts) < 3:
                                sock.sendall(b"ERROR: Usage: /upload <filename> <size>\n")
                                continue
                                
                            filename = parts[1]
                            file_size = int(parts[2])
                            
                            filepath = os.path.join(FILE_DIR, filename)
                            print(f"[Server] Preparing vault for {filename} ({file_size} bytes)")

                            received = 0
                            with open(filepath, 'wb') as f:
                                while received < file_size:
                                    chunk = sock.recv(min(BUFF_SIZE, file_size - received))
                                    if not chunk: break
                                    f.write(chunk)
                                    received += len(chunk)
                            
                            sock.sendall(f"UPLOAD OK: {filename} secured.\n".encode())
                        except (IndexError, ValueError):
                            sock.sendall(b"ERROR: Invalid upload command format.\n")

                    # DOWNLOAD FEATURE
                    elif li.startswith('/download'):
                        try:
                            parts = li.split()
                            if len(parts) < 2:
                                sock.sendall(b"ERROR: Usage: /download <filename>\n")
                                continue
                                
                            filename = parts[1]                        
                            filepath = os.path.join(FILE_DIR, filename)

                            if os.path.exists(filepath):
                                file_size = os.path.getsize(filepath)
                                print(f"[Rivendell] dispatched '{filename}' ({file_size} bytes)")

                                header = f"/incoming {filename} {file_size}".ljust(BUFF_SIZE)
                                sock.sendall(header.encode())

                                with open(filepath, "rb") as f:
                                    while True:
                                        chunk = f.read(BUFF_SIZE)
                                        if not chunk: break
                                        sock.sendall(chunk)
                            else:
                                sock.sendall(f"ERROR: The scroll '{filename}' is not in the archives.\n".encode())
                        except IndexError:
                            sock.sendall(b"ERROR: Usage: /download <filename>\n")
                    else:
                        sock.sendall(f"[Lord Elrond Echo]: {li}\n".encode())
                    
                except ConnectionResetError:
                    print("The gates are barred. Is the Rivendell server awake? (Connection Reset)")
                    if sock in inputs: inputs.remove(sock)
                    sock.close()
if __name__ == "__main__":
    main()