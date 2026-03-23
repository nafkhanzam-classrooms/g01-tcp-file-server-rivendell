import socket

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
