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
    ID = message[0:2]                      # get ID and QR
    demessage = list(message)
    header = demessage[2]
    biheader = bin(header)[2:].rjust(8, '0')
    QR = biheader[0]

    if QR == "0":                         # if the message is a query
        QDCount = demessage[4:6]          # get the original QName and the QType and convert them into readable ones
        QName = demessage[12: len(demessage)-16]
        QType = demessage[len(demessage)-15:len(demessage)-13]
        a = 0
        parts = []
        while a < len(QName) and QName[a]:      # convert QName
            leng = QName[a]                     # leng is the length of str between dots
            offset = a + 1
            temp = ""
            for i in range(offset, offset+leng):
                temp += chr(QName[i])
            parts.append(temp)
            a = offset + leng
        qname2 = ".".join(parts)
        qtype2 = QType[0]*2 + QType[1]          # convert QType
        temp = (ID, qname2, qtype2)
        for i in range(0, len(query)):          # check if it is in the cache
            if query[i][1:3] == temp[1:3]:      # if in the cache, change the ID and send back info
                t = response[i][0:2]
                tosend = response[i].replace(t, ID, 1)
                serverSocket.sendto(tosend, clientAddress)
                print("Info is in cache.")      # print a prompt
                continue

        query.insert(len(query), temp)          # if not, add to query record and send query to upper server
        temp = (ID, clientAddress)
        toReply.insert(len(toReply), temp)      # add the query to the to-reply list
        serverSocket.sendto(message, (upserver, serverPort))

    elif QR == "1":                             # if the message is a response
        for i in range(0, len(toReply)):        # check if the response is in to-reply list
            if ID == toReply[i][0]:             # if it is
                serverSocket.sendto(message, toReply[i][1])     # reply and delete it from the list
                del toReply[i]                                  # also add it to response records
                for j in range(0, len(query)):
                    if query[j][0] == ID:
                        response.insert(j, message)
