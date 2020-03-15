from socket import *


serverPort = 53
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))
upserver = "ns2.sustech.edu.cn"
print("The server is ready to receive.")

query = []      # it stores the query records
response = []   # it stores the response records
toReply = []    # it stores the replies that the resolver need to make

while True:
    message, clientAddress = serverSocket.recvfrom(2048)

    # demessage = int.from_bytes(bytes(message), byteorder="big")

    ID = message[0:2]       # get ID and QR
    header = int(ord(message[2]))
    biheader = bin(header)[2:].rjust(8, '0')
    QR = biheader[0]

    if QR == "0":           # if the message is a query
        QDCount = message[4:6]          # get the original QName and the QType and convert them into readable ones
        QName = message[12: len(message)-16]
        QType = message[len(message)-15:len(message)-13]
        a = 0
        parts = []
        while a < len(QName) and QName[a]:      # convert QName
            leng = int(ord(QName[a]))           # leng is the length of str between dots
            offset = a + 1
            parts.append(QName[offset:offset+leng])
            a = offset + leng
        qname2 = ".".join(parts)
        # qtype2 = int(ord(QType[0]))*2+int(ord(QType[1]))    # convert QType
        qtype2 = int(ord(QType))    # convert QType
        # print("qtype2:{}".format(qtype2))
        temp = (ID, qname2, qtype2)
        for i in range(0, len(query)):          # check if it is in the cache
            if query[i][1:3] == temp[1:3]:      # if in the cache, change the ID and send back info
                t = response[i][0:2]
                response[i].replace(t, message[0:2], 1)
                serverSocket.sendto(response[i], clientAddress)
                print("Info is in cache.")      # print a prompt
                continue

        query.insert(len(query), temp)          # if not, add to query record and send query to upper server
        temp = (ID, clientAddress)
        toReply.insert(len(toReply), temp)      # add the query to the to-reply list
        serverSocket.sendto(message, (upserver, serverPort))

    elif QR == "1":               # if the message is a response
        for i in range(0, len(toReply)):        # check if the response is in to-reply list
            if ID == toReply[i][0]:             # if it is
                serverSocket.sendto(message, toReply[i][1])     # reply and delete it from the list
                del toReply[i]                                  # also add it to response records
                for j in range(0, len(query)):
                    if query[j][0] == ID:
                        response.insert(j, message)

# 102971672414337509524647501724452429032027154971557899857297360510465606311715287551410554627271163904