import socket
import os

HOST = '127.0.0.1'
PORT = 8888
ADDR = (HOST, PORT)
BUFF_SIZE = 1024

def unique(filename):
    if not os.path.exists(filename): return filename
    
    name, ext = os.path.splitext(filename)
    counter = 1
    
    new_filename = f"{name}({counter}){ext}"
    while os.path.exists(new_filename):
        counter += 1
        new_filename = f"{name}({counter}){ext}"
        
    return new_filename

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(ADDR)
        print(f"Welcome to Rivendell! Entering the Gates of [{HOST}:{PORT}]")

        while True:
            message = input("> ")
            if not message: continue

            # UPLOAD FEATURE
            if message.startswith('/upload'):
                try:
                    parts = message.split()
                    filepath = parts[1]
                    
                    if os.path.exists(filepath):
                        filename = os.path.basename(filepath)
                        filesize = os.path.getsize(filepath)
                        header = f"/upload {filename} {filesize}".ljust(BUFF_SIZE)
                        client.sendall(header.encode())
                        
                        with open(filepath, "rb") as f:
                            while True:
                                chunk = f.read(BUFF_SIZE)
                                if not chunk: break
                                client.sendall(chunk)
                        print(f"[Client] Blast! Sending {filename} ({filesize} bytes)...")
                        response = client.recv(BUFF_SIZE)
                        print(response.decode(errors='ignore').strip())
                    else:
                        print("The archives hold no such record. (File not found locally)")
                        continue
                except IndexError:
                    print("Even the wise must name their burden. Usage: /upload <filename>")
                    continue

            # DOWNLOAD FEATURE
            elif message.startswith('/download'):
                try:
                    header = message.ljust(BUFF_SIZE)
                    client.sendall(header.encode())

                    response = client.recv(BUFF_SIZE)
                    header_text = response.decode(errors='ignore').strip()
                    
                    if header_text.startswith('/incoming'):
                        parts = header_text.split()
                        original_filename = parts[1]
                        filesize = int(parts[2])

                        saved_path = unique(original_filename)
                        
                        print(f"[Client] Receiving scroll: '{saved_path}' ({filesize} bytes)...")
                        received = 0
                        with open(saved_path, "wb") as f:
                            while received < filesize:
                                chunk = client.recv(min(BUFF_SIZE, filesize - received))
                                if not chunk: break
                                f.write(chunk)
                                received += len(chunk)
                                
                        print(f"[Client] Successfully received '{saved_path}'!")

                    else: print(header_text)
                except IndexError:
                    print("ERROR: Usage: /download <filename>")
            else:
                header = message.ljust(BUFF_SIZE)
                client.sendall(header.encode())

                data = client.recv(BUFF_SIZE)

                if not data:
                    print("The connection was severed.")
                    break

                print(data.decode().strip())
                if message.lower() == 'exit': break

    except ConnectionRefusedError:
        print("The gates are barred. Is the Rivendell server awake? (Connection Refused)")
        return
    finally:
        client.close()

if __name__ == "__main__":
    main()
