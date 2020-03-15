from socket import *

serverName = '127.0.0.1'
serverPort = 53
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = input('Input the hostname and the DNS type: ')
clientSocket.sendto(message.encode(), (serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())
clientSocket.close()

