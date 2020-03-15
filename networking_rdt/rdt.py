from udp import UDPsocket
import signal


class socket(UDPsocket):
    WINDOW_SIZE = 6
    TIMEOUT = 0.8
    # set the sending window size and timer for timeout

    def __init__(self):
        super(socket, self).__init__()
        self.expect_seq = 0
        self.current_seq = 0
        self.buffer = []
        # expect_seq is the expecting sequence num for the next packet to receive
        # current_seq is the sequence num for next packet to send
        # buffer stores the sequence num of packets to be acked

    # def connect(self):
    #     # send syn; receive syn, ack; send ack
    #     # your code here
    #     pass
    #
    # def accept(self):
    #     # receive syn; send syn, ack; receive ack
    #     # your code here
    #     pass
    #
    # def close(self):
    #     # send fin; receive ack; receive fin; send ack
    #     # your code here
    #     pass

    def recvfrom(self):
        # this function is to receive the data
        rcv_data = b''
        # rcv_data stores all the data received
        while True:
            # receive packets
            raw_data, address = super().recvfrom(segment.SEGMENT_LEN)
            data = segment.parse_segment(raw_data)
            # parse the data received
            checksum = segment.checksum(raw_data)
            # calculate the checksum of the received data
            if not data[2]:
                # if the ack flag is true
                if data[5] != len(raw_data) or checksum != 0:
                    # if the there are bit errors
                    print("bit error")
                    retrans = segment(self.current_seq, self.expect_seq, b'', False, False, True).create_segment()
                    super().sendto(retrans, address)
                    # retransmit the ack
                elif data[1] == 1:
                    # if the received packet is a fin packet
                    break
                elif data[3] != self.expect_seq:
                    # if the sequence num does not match the expected sequence num
                    print("seq error")
                    retrans = segment(self.current_seq, self.expect_seq, b'', False, False, True).create_segment()
                    super().sendto(retrans, address)
                else:
                    # otherwise the packet is the correct packet, print a prompt
                    rcv_data += data[7]
                    print("ack")
                    # sotre the received data
                    self.expect_seq += len(data[7])
                    self.expect_seq = self.expect_seq % segment.MAX_SEQ
                    # change the expected sequence num
                    ack = segment(self.current_seq, self.expect_seq, b'', False, False, True).create_segment()
                    super().sendto(ack, address)
                    # make an ack
        self.expect_seq = 0
        return rcv_data, address

    def send_packet(self, data: bytes, address: tuple, offset: int):
        # this function is to send a specific packet
        if len(data) >= segment.MAX_PAYLOAD + offset:
            # if not reaching end of sending buffer
            partial_data = data[offset:offset + segment.MAX_PAYLOAD]
            packet = segment(offset, self.expect_seq, partial_data, False, False, False).create_segment()
            super().sendto(packet, address)
            # send packet
            return True
        else:
            # if reaching end of sending buffer
            partial_data = data[offset:]
            fin = segment(offset, self.expect_seq, partial_data, False, False, False).create_segment()
            super().sendto(fin, address)
            return False

    def timeout(self, signum, frame):
        # this function raise a TimeoutError
        raise TimeoutError

    def rcv_packet(self):
        # this function is for the sender to receive an ack
        signal.signal(signal.SIGALRM, self.timeout)
        signal.setitimer(signal.ITIMER_REAL, socket.TIMEOUT)
        # set a timer
        try:
            while True:
                # try to receive a packet and check whether there is bit error
                raw_data, address = super().recvfrom(segment.SEGMENT_LEN)
                parse_data = segment.parse_segment(raw_data)
                checksum = segment.checksum(raw_data)
                if parse_data[5] == len(raw_data) and checksum == 0:
                    if parse_data[2] and parse_data[4] in self.buffer:
                        # if no bit error and the ack num is in sequence nums of packets to be acked
                        if parse_data[4] > self.current_seq:
                            self.current_seq = parse_data[4]
                            # change the sending base
                        for i in self.buffer:
                            if i <= parse_data[4]:
                                self.buffer.remove(i)
                                # remove the acked packet from the to-be-acked list
                        if len(self.buffer) == 0:
                            signal.setitimer(signal.ITIMER_REAL, 0)
                            # if all packets are acked, stop the timer
                            break
        except TimeoutError:
            print("timeout")
            self.buffer.clear()

    def sendto(self, data: bytes, address: tuple):
        # this function is to send data
        while True:
            for i in range(0, socket.WINDOW_SIZE):
                # window_size is the sending window size
                if not self.send_packet(data, address, self.current_seq + segment.MAX_PAYLOAD*i):
                    self.buffer.append(len(data))
                    # send the packet. if reaching end of sending buffer,
                    # put sequence num into to-be-acked list and break
                    break
                self.buffer.append(self.current_seq + segment.MAX_PAYLOAD*(i+1))
                # put sequence num into to-be-acked list
            self.rcv_packet()
            # try to receive ack
            if self.current_seq == len(data):
                fin = segment(self.current_seq, self.expect_seq, b'', False, True, False).create_segment()
                for i in range(0, 5):
                    super().sendto(fin, address)
                    # if all data is sent, send a fin packet to inform the receiver to disconnect
                    # beacause the receiving channal is always unstable,
                    # the successful receiving of the fin packet can not be guarenteed.
                    # sending the fin packets 5 times increases the possibility of successful receiving to
                    # about 97%
                self.current_seq = 0
                break
                # disconnect


class segment:
    HEADER_LEN = 15
    # the length of header
    MAX_PAYLOAD = 1485
    # the max payload
    MAX_SEQ = 4294967295
    # the max sequence num
    SEGMENT_LEN = 1500
    # the total length of segment

    def __init__(self, seq_num: int, ack_num: int, payload: bytes,
                 syn: bool = False, fin: bool = False, ack: bool = False):
        self.syn = syn
        self.fin = fin
        self.ack = ack
        self.seq_num = seq_num % segment.MAX_SEQ
        self.ack_num = ack_num % segment.MAX_SEQ
        self.payload = payload
        self.leng = len(self.payload) + segment.HEADER_LEN
        # initialize parts of segment

    def create_segment(self):
        # this funciton creates a segment
        flag = 0x00
        if self.syn:
            flag |= 0x04
        if self.fin:
            flag |= 0x02
        if self.ack:
            flag |= 0x01
        # set the flags
        temp = 0
        arr = flag.to_bytes(1, byteorder='big') + self.seq_num.to_bytes(4, byteorder='big') \
            + self.ack_num.to_bytes(4, byteorder='big') + self.leng.to_bytes(4, byteorder='big') \
            + temp.to_bytes(2, byteorder='big') + self.payload
        checksum = segment.checksum(arr)
        # checksum = checksum.to_bytes(2, byteorder='big')
        # calculate the checksum
        arr = flag.to_bytes(1, byteorder='big') + self.seq_num.to_bytes(4, byteorder='big') \
            + self.ack_num.to_bytes(4, byteorder='big') + self.leng.to_bytes(4, byteorder='big') \
            + checksum.to_bytes(2, byteorder='big') + self.payload
        return arr
        # return the segment

    @staticmethod
    def parse_segment(arr: bytes):
        # this function parse the received segment
        flag = arr[0]
        syn = (flag & 0x04) != 0
        fin = (flag & 0x02) != 0
        ack = (flag & 0x01) != 0
        seq_num = int.from_bytes(bytes(arr[1:5]), byteorder='big')
        ack_num = int.from_bytes(bytes(arr[5:9]), byteorder='big')
        leng = int.from_bytes(bytes(arr[9:13]), byteorder='big')
        checksum = arr[13:15]
        payload = arr[15:]
        return syn, fin, ack, seq_num, ack_num, leng, checksum, payload

    @staticmethod
    def carry_around_add(a, b):
        c = a + b
        return (c & 0xffff) + (c >> 16)

    @staticmethod
    def checksum(msg: bytes):
        # this function calculate the checksum
        s = 0
        for i in range(0, len(msg), 2):
            if i+1 < len(msg):
                w = msg[i] + (msg[i + 1] << 8)
            else:
                w = msg[i]
            s = segment.carry_around_add(s, w)
        return ~s & 0xffff
