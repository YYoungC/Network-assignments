from rdt import socket

SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 8080
client = socket()
client.connect((SERVER_ADDR, SERVER_PORT))
with open('alice.txt', 'rb') as f:
    DATA = f.read()
    # reads a file
client = socket()
print("start sending")
client.sendto(DATA, (SERVER_ADDR, SERVER_PORT))
# send data
print("start rcving")
data, server_addr = client.recvfrom()
# receive data
assert data == DATA
print("hooray")
# if the data received equals data sent, print a prompt
