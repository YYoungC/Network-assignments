import asyncio
import os
import urllib.request
import mimetypes
import urllib.parse


class Resolver(object):
    def __init__(self, dataline):
        self.cookie = {}
        self.dataline = dataline
        self.header = ""
        self.part_range = None
        self.method = ""
        self.path = ""
        # initialize variables
        for a in self.dataline:
            self.parse_header(a)
        # get the method, path, etc from header
        if self.path:
            self.path = urllib.parse.unquote(self.path)
        # parse the path
        self.conn = "Connection: close\r\n"
        self.line = "\r\n"
        self.status = ["HTTP/1.0 200 OK\r\n", "HTTP/1.0 206 Partial Content\r\n",
                       "HTTP/1.0 302 Found\r\n",
                       "HTTP/1.0 404 Not Found\r\n", "HTTP/1.0 405 Method Not Allowed\r\n"]
        self.body = b''
        self.set_header()
        # get the response header and store it in self.header

    def get_range(self, string):
        # get the range in request
        start = None
        end = None
        parts = string.split('=')
        if parts[0] == 'bytes':
            range = parts[1].split('-')
            if range[0] != '':
                start = int(range[0])
            else:
                start = 0
            if range[1] != '':
                end = int(range[1])
            else:
                end = -1
        if start is not None and end is not None:
            return start, end
        else:
            return None

    def set_cookie(self, string):
        # get cookies from header
        parts = string.split(';')
        for i in parts:
            entry = i.split('=')
            self.cookie[entry[0]] = entry[1]

    def get_cookie(self, entry):
        # get cookies by name
        if entry in self.cookie:
            return self.cookie[entry]
        else:
            return None

    def parse_header(self, line):
        # parse the header
        parts = line.split(' ')
        if parts[0] == 'GET' or parts[0] == 'HEAD':
            self.method = parts[0]
            self.path = parts[1]
        if parts[0] == 'Range:':
            self.part_range = self.get_range(parts[1][:-2])
        if parts[0] == 'Cookie:':
            self.set_cookie(parts[1][:-2])

    def set_header(self):
        if (self.path == '/' or self.path == "") and self.cookie and self.get_cookie('last'):
            # if path is root path and cookie available, change the path and set the header
            self.path = self.get_cookie('last')
            self.header = self.status[2] + "Location: " + self.path + self.line + self.conn
        else:
            # first time enter root path, return the dir of the current file
            if self.path == "/" or self.path == "":
                self.path = os.getcwd()
            if os.path.isdir(self.path):
                # if the path is a dir, set the cookie and type
                cook = "Set-Cookie: last=" + self.path + "; Path=/\r\n"
                type = "Content-Type: text/html; charset=utf-8\r\n"
                self.header = self.status[0] + type + cook + self.conn
            elif os.path.isfile(self.path):
                # if the path is a file
                url = urllib.request.pathname2url(self.path)
                mimety = mimetypes.guess_type(url)
                # get mime type
                lent = os.path.getsize(self.path)
                # get the length of the file
                type = "Content-Type: " + str(mimety[0]) + "; charset=utf-8\r\n"
                acc = 'Accept-Range: bytes\r\n'
                if self.part_range is not None:
                    # if request contains range
                    print("part:{}".format(self.part_range))
                    start = self.part_range[0]
                    end = self.part_range[1]
                    if end < 0:
                        end = lent + end
                    crange = "Content-Range: " + str.format('bytes %d-%d/%d' % (start, end, lent)) + "\r\n"
                    length = "Content-Length: " + str(end - start + 1) + "\r\n"
                    self.header = self.status[1] + type + acc + crange + length + self.conn
                else:
                    length = "Content-Length: " + str(lent) + "\r\n"
                    self.header = self.status[0] + type + acc + length + self.conn
            else:
                # if request method invalid
                self.error(404)

    def get_body(self):
        # this function returns the body of response
        if os.path.isdir(self.path):
            # if path is a dir
            back = os.path.dirname(self.path)
            # get the former dir
            h1 = "<html><head><title>Index of " + self.path + "</title></head>\r\n" \
                 "<body bgcolor=\"white\">\r\n" \
                 "<h1>Index of " + self.path + "</h1><hr>\r\n" \
                 "<pre>\r\n"
            h2 = "<a href=\"" + back + "\">../</a>\r\n"
            h3 = "</pre>\r\n" \
                 "<hr>\r\n" \
                 "</body></html>\r\n"
            dirs = os.listdir(self.path)
            # get the list of the dirs and files of the current dir
            for i in range(0, len(dirs)):
                # add them to the html
                checkpath = self.path + "/" + dirs[i]
                if os.path.isfile(checkpath):
                    h2 += "<a href=\"" + checkpath + "\">" + dirs[i] + "</a>\r\n"
                else:
                    h2 += "<a href=\"" + checkpath + "\">" + dirs[i] + "/</a>\r\n"
            h = h1 + h2 + h3
            self.body = h + "\r\n"
            return self.body.encode()
        elif os.path.isfile(self.path):
            # if path is a file
            lent = os.path.getsize(self.path)
            if self.part_range is not None:
                # if request contains range
                start = self.part_range[0]
                end = self.part_range[1]
                if end < 0:
                    end = lent + end
                file = open(self.path, 'rb')
                # open the file and write it
                file.seek(start, 0)
                return file.read(end - start + 1)
            else:
                file = open(self.path, 'rb')
                return file.read()
        else:
            return self.body

    def error(self, stat):
        # this function set the header if error occurs
        if stat == 404:
            self.header = self.status[3] + self.conn
        elif stat == 405:
            self.header = self.status[4] + self.conn

    def get_response(self):
        # this funciton returns repsonse
        if self.method == "HEAD":
            return (self.header + "\r\n").encode()
        elif self.method == "GET":
            return (self.header + "\r\n").encode() + self.get_body()
        else:
            self.error(405)
            return (self.header + "\r\n").encode()


async def dispatch(reader, writer):
    dataline = []
    while True:
        # read the data
        data = await reader.readline()
        dataline.append(data.decode())
        if data == b'\r\n' or data == b'':
            break

    resolver = Resolver(dataline)
    writer.write(resolver.get_response())

    await writer.drain()
    writer.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(dispatch, '127.0.0.1', 8080, loop=loop)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
