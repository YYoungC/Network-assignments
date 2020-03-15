from rdt import socket

SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 8080
server = socket()
server.bind((SERVER_ADDR, SERVER_PORT))
server = socket()
server.bind((SERVER_ADDR, SERVER_PORT))
while True:
    print("start rcving")
    data, client_addr = server.recvfrom()
    # receive data
    print("start sending")
    server.sendto(data, client_addr)
    # send data back

