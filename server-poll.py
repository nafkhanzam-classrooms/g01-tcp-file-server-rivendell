import socket
import os
import select

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

    poller = select.poll()
    
    poller.register(server.fileno(), select.POLLIN)

    fd_to_socket = { server.fileno(): server,
               }

    while True:
        events = poller.poll()

        for fd, ev in events:
            sock = fd_to_socket[fd]
            if sock is server:
                connection, address = server.accept()
                connection.setblocking(0)

                poller.register(connection.fileno(), select.POLLIN)
                fd_to_socket[connection.fileno()] = connection

            elif ev & select.POLLIN:
                try:
                    data = sock.recv(BUFF_SIZE)

                    if not data:
                        print(f"Emissary {sock.getpeername()} gracefully departed.")
                        poller.unregister(fd)
                        del fd_to_socket[fd]
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
                    poller.unregister(fd)
                    if fd in fd_to_socket: del fd_to_socket[fd]
                    sock.close()
if __name__ == "__main__":
    main()