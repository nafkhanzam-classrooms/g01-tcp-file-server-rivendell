import socket
import os
import threading

HOST = '127.0.0.1'
PORT = 8888
ADDR = (HOST, PORT)
FILE_DIR = 'server_folder'
BUFF_SIZE = 1024

if not os.path.exists(FILE_DIR): os.makedirs(FILE_DIR)

def client_handling(connection, address):
    print(f"Connected by {address}")

    try:
        with connection:
            while True:
                data = connection.recv(BUFF_SIZE)
                if not data: break

                lines = data.decode(errors='ignore').split('\n')
                for li in lines:
                    li = li.strip()
                    if not li: continue
                    
                    # LIST FEATURE
                    if li.startswith('/list'):
                        files = os.listdir(FILE_DIR)
                        response = "Archives:\n" + "\n".join(files) + "\n"
                        connection.sendall(response.encode())

                    # UPLOAD FEATURE
                    elif li.startswith('/upload'):
                        try:
                            parts = li.split()
                            if len(parts) < 3:
                                connection.sendall(b"ERROR: Usage: /upload <filename> <size>\n")
                                continue
                                
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
                        except (IndexError, ValueError):
                            connection.sendall(b"ERROR: Invalid upload command format.\n")

                    # DOWNLOAD FEATURE
                    elif li.startswith('/download'):
                        try:
                            parts = li.split()
                            if len(parts) < 2:
                                connection.sendall(b"ERROR: Usage: /download <filename>\n")
                                continue
                                
                            filename = parts[1]                        
                            filepath = os.path.join(FILE_DIR, filename)

                            if os.path.exists(filepath):
                                file_size = os.path.getsize(filepath)
                                print(f"[Rivendell] dispatched '{filename}' ({file_size} bytes)")

                                header = f"/incoming {filename} {file_size}".ljust(BUFF_SIZE)
                                connection.sendall(header.encode())

                                with open(filepath, "rb") as f:
                                    while True:
                                        chunk = f.read(BUFF_SIZE)
                                        if not chunk: break
                                        connection.sendall(chunk)
                            else:
                                connection.sendall(f"ERROR: The scroll '{filename}' is not in the archives.\n".encode())
                        except IndexError:
                            connection.sendall(b"ERROR: Usage: /download <filename>\n")

                    else: 
                        connection.sendall(f"[Lord Elrond Echo]: {li}\n".encode())

    except ConnectionResetError:
        print("The gates are barred. Is the Rivendell server awake? (Connection Reset)")
    finally:
        print(f"{address} disconnected")
    
def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ADDR)
    server.listen(5)
    print(f"[PALANTIR] has activated multi-threading")

    while True:
        connection, address = server.accept()
        client_threading = threading.Thread(target=client_handling, args=(connection,address))

        client_threading.daemon = True
        client_threading.start()
if __name__ == "__main__":
    main()