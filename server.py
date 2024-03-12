import socket
import threading
import ssl

# Server setup
HOST = '192.0.0.2'
PORT = 1234
clients = []

def client_handler(client_socket, address):
    print(f"Connection from {address} has been established.")
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            if len(clients) == 1:
                # If this is the only connected client, send a notification
                try:
                    client_socket.sendall("No other clients connected.".encode())
                except BrokenPipeError:
                    break  # Client disconnected
            else:
                # Relay data to all other clients
                for other_client in clients:
                    if other_client != client_socket:
                        other_client.sendall(data)
    finally:
        client_socket.close()
        clients.remove(client_socket)
        print(f"Connection from {address} closed.")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Server listening on {HOST}:{PORT}")

        # Wrap the server socket with SSL context
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile='server_certificate.pem', keyfile='server_key.pem')
        server_socket = ssl_context.wrap_socket(server_socket, server_side=True)

        # Start the server
        while True:
            client_socket, address = server_socket.accept()
            clients.append(client_socket)
            thread = threading.Thread(target=client_handler, args=(client_socket, address))
            thread.start()

if __name__ == "__main__":
    main()
