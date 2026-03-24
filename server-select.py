import socket
import select

HOST = '127.0.0.1'
PORT = 8888
ADDR = (HOST, PORT)
FILE_DIR = 'server_folder'
BUFF_SIZE = 1024

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
                    if data:
                        li = data.decode('utf-8', errors='ignore').strip()
                        sock.sendall(f"[Lord Elrond Echo]: {li}\n".encode())
                    else:
                        print(f"Emissary {sock.getpeername()} gracefully departed.")
                        inputs.remove(sock)
                        sock.close()
                except ConnectionResetError:
                    print("The gates are barred. Is the Rivendell server awake? (Connection Reset)")
                    inputs.remove(sock)
                    sock.close()
if __name__ == "__main__":
    main()