import socket
import os

HOST = '127.0.0.1'
PORT = 8888

ADDR = (HOST, PORT)

BUFF_SIZE = 1024

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
                        header = f"/upload {filename} {filesize}\n"
                        client.sendall(header.encode())
                        
                        with open(filepath, "rb") as f:
                            while True:
                                chunk = f.read(BUFF_SIZE)
                                if not chunk: 
                                    break
                                client.sendall(chunk)
                        print(f"[Client] Blast! Sending {filename} ({filesize} bytes)...")
                    else:
                        print("The archives hold no such record. (File not found locally)")
                        continue
                except IndexError:
                    print("Even the wise must name their burden. Usage: /upload <filename>")
                    continue

            else: 
                client.sendall((message + '\n').encode())
            
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
