import socket, threading

class Communication:

    state = 1
    def __init__(self):
        print("Server is created...")
        with open("txt\change.txt", "w") as doc:
            doc.write("1")
        self.learn()

    def learn(self):

        while 1:
            with open("txt\change.txt", "r") as doc:
                self.state = doc.read()
            if "SOCK" in self.state: break

        if "STREAM" in self.state: TCP()
        elif "DGRAM" in self.state: UDP()

class TCP:

    clients_list = []
    last_received_message = ""

    def __init__(self):
        self.server_socket = None
        self.listening_server()

    def listening_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        IP =  socket.gethostbyname("0.0.0.0")
        PORT = 54321

        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((IP, PORT))
        print("Listening for incoming messages...")
        self.server_socket.listen(5)
        self.new_thread()

    def new_thread(self):

        while True:
            client = so, (ip, port) = self.server_socket.accept()
            if client not in self.clients_list: self.clients_list.append(client)
            print(f'{ip} connected from {port}')

            thread = threading.Thread(target=self.receive_messages, args=(so, ))
            thread.start()

    def receive_messages(self, so):

        while True:
            incoming_buffer = so.recv(1024)

            if not incoming_buffer: break

            self.last_received_message = incoming_buffer

            self.broadcast(so)  # send to all clients

        so.close()

    def broadcast(self, senders_socket):
        for client in self.clients_list:
            soc = client[0]
            if soc is not senders_socket:
                soc.send(self.last_received_message)

class UDP:
    clients_list = []
    last_received_message = ""

    def __init__(self):
        self.create_server()

    def create_server(self):
        IP = socket.gethostbyname("0.0.0.0")
        PORT = 54321
        self.UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.UDPServerSocket.bind((IP, PORT))
        self.UDPServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print("Listening for incoming messages...")

        self.receive()

    def receive(self):

        while True:

            bytesAddressPair = self.UDPServerSocket.recvfrom(1024)
            message = bytesAddressPair[0]
            address = bytesAddressPair[1]

            self.last_received_message = message

            if address not in self.clients_list:
                self.clients_list.append(address)
                print(f'{address[0]} connected from {address[1]}')

            self.broadcast(address)

    def broadcast(self, senders_socket):
        for client in self.clients_list:
            if client == senders_socket: continue

            self.UDPServerSocket.sendto(self.last_received_message, client)

if __name__ == '__main__':
    Communication()