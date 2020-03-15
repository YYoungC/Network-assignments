# this is assignment 4.2

import asyncio
import os
import urllib.request
import mimetypes
import urllib.parse


async def dispatch(reader, writer):
    keys = ('method', 'path', 'range', 'cookie')
    headers_data = []
    headers = {key: None for key in keys}
    cookie = {}

    def get_range(string):
        start = None
        end = None
        parts = string.split('=')
        if parts[0] == 'bytes':
            range_int = parts[1].split('-')
            if range_int[0] != '':
                start = int(range_int[0])
            else:
                start = 0
            if range_int[1] != '':
                end = int(range_int[1])
            else:
                end = -1
        if start is not None and end is not None:
            return start, end
        else:
            return None

    def set_cookie(string):
        items = string.split(';')
        for i in items:
            entry = i.split('=')
            cookie[entry[0]] = entry[1]

    def get_cookie(entry):
        if entry in cookie:
            return cookie[entry]
        else:
            return None

    def parse_header(line):
        fields = line.split(' ')
        if fields[0] == 'GET' or fields[0] == 'POST' or fields[0] == 'HEAD':
            headers['method'] = fields[0]
            headers['path'] = fields[1]
        if fields[0] == 'Range:':
            headers['range'] = get_range(fields[1][:-2])
        if fields[0] == 'Cookie:':
            set_cookie(fields[1][:-2])

    def send(path, meth):  # if the requested dir is a file, invoke this function
        url = urllib.request.pathname2url(path)  # get the type of the file
        mimety = mimetypes.guess_type(url)
        lent = os.path.getsize(path)  # get the length of the file
        if part_range is None:
            status = "HTTP/1.0 200 OK"  # the following are the response
        else:
            status = "HTTP/1.0 206 Partial Content"
        type = "Content-Type: " + str(mimety[0]) + "; charset=utf-8"
        acc = 'Accept-Range: bytes'
        conn = "Connection: close"
        line = b''
        stri = b'\r\n'
        if part_range is not None:
            start, end = part_range[0], part_range[1]
            if end < 0:
                end = lent + end
            crange = "Content-Range: " + str.format('bytes %d-%d/%d' % (start, end, lent))
            length = "Content-Length: " + str(end - start + 1)
            if meth == "GET":  # if the method is get
                seq = (bytes(status, encoding="utf-8"), bytes(type, encoding="utf-8"), bytes(acc, encoding="utf-8"),
                       bytes(crange, encoding="utf-8"),
                       bytes(length, encoding="utf-8"),
                       bytes(conn, encoding="utf-8"), line, line)
                writer.writelines(  # turn the response into bytes and write them
                    [stri.join(seq)]
                )
                file = open(path, 'rb')  # open the file and write it
                file.seek(start, 0)
                writer.write(file.read(end - start + 1))
            elif meth == "Head":  # if the method is head
                seq = (bytes(status, encoding="utf-8"), bytes(type, encoding="utf-8"), bytes(acc, encoding="utf-8"),
                       bytes(acc, encoding="utf-8"),
                       bytes(length, encoding="utf-8"),
                       bytes(conn, encoding="utf-8"), line)
                writer.writelines(  # turn the response into bytes and write them
                    [stri.join(seq)]
                )

        else:
            length = "Content-Length: " + str(lent)
            if meth == "GET":  # if the method is get
                seq = (bytes(status, encoding="utf-8"), bytes(type, encoding="utf-8"), bytes(acc, encoding="utf-8"), bytes(length, encoding="utf-8"),
                       bytes(conn, encoding="utf-8"), line, line)
                writer.writelines(  # turn the response into bytes and write them
                    [stri.join(seq)]
                )
                file = open(path, 'rb')  # open the file and write it
                writer.write(file.read())
            elif meth == "Head":  # if the method is head
                seq = (bytes(status, encoding="utf-8"), bytes(type, encoding="utf-8"), bytes(acc, encoding="utf-8"), bytes(length, encoding="utf-8"),
                       bytes(conn, encoding="utf-8"), line)
                writer.writelines(  # turn the response into bytes and write them
                    [stri.join(seq)]
                )

    def sendir(path, re = 0):  # if the requested dir is a dir, invoke this function
        if re == 0:
            status = "HTTP/1.0 200 OK"  # the following are the response
        else:
            status = "HTTP/1.0 302 Found"
        addr = "Location: " + path
        type = "Content-Type:text/html; charset=utf-8"
        cook = "Set-Cookie: last=" + path + "; Path=/"
        conn = "Connection: close"
        line = b''
        back = os.path.dirname(path)  # get the former dir
        h1 = "<html><head><title>Index of " + path + "</title></head>" \
                                                     "<body bgcolor=\"white\">" \
                                                     "<h1>Index of " + path + "</h1><hr>" \
                                                                              "<pre>"
        h2 = "<a href=\"" + back + "\">../</a><br>"
        h3 = "</pre>" \
             "<hr>" \
             "</body></html>"
        dirs = os.listdir(path)  # get the list of the dirs and files of the current dir
        for i in range(0, len(dirs)):  # add them to the html
            checkpath = path + "/" + dirs[i]
            if os.path.isfile(checkpath):
                h2 += "<a href=\"" + checkpath + "\">" + dirs[i] + "</a><br>"
            else:
                h2 += "<a href=\"" + checkpath + "\">" + dirs[i] + "/</a><br>"
        h = h1 + h2 + h3
        stri = b'\r\n'
        if re == 0:
            seq = (bytes(status, encoding="utf-8"), bytes(type, encoding="utf-8"), bytes(cook, encoding="utf-8"), bytes(conn, encoding="utf-8"), line,
                   bytes(h, encoding="utf-8"), line)
        else:
            seq = (bytes(status, encoding="utf-8"), bytes(addr, encoding="utf-8"), bytes(conn, encoding="utf-8"), line)
        writer.writelines(  # turn the response into bytes and write them
            [stri.join(seq)]
        )

    def error(sta):  # if error occurs, invoke this function
        status = ""
        if sta == 405:  # if it is a 405 error
            status = "HTTP/1.0 405 Method Not Allowed"
        elif sta == 404:  # if it is a 405 error
            status = "HTTP/1.0 404 Not Found"
        stri = b'\r\n'
        line = b''
        seq = (str.encode(status), line)
        writer.writelines(  # write the response
            [stri.join(seq)]
        )

    while True:
        data = await reader.readline()
        headers_data.append(data.decode())
        # print(data)
        if data == b'\r\n' or data == b'':
            break

    for line in headers_data:
        parse_header(line)

    method = headers.get('method')
    if headers.get('path'):
        path = urllib.parse.unquote(headers.get('path'))
    part_range = headers.get('range')
    # print(path)
    # print(get_cookie('last'))

    if (path == '/' or path == "") and cookie and get_cookie('last') and get_cookie('last') != '/':
        # print("cookie")
        path = get_cookie('last')
        sendir(path, 1)
    else:
        if path == "/" or path == "":  # return the dir of the current file
            path = os.getcwd()
        if os.path.isfile(path):  # if the dir is a file
            if method == "GET":  # if the method is get
                try:
                    send(path, "GET")
                except FileNotFoundError:  # deal with error
                    error(404)
            elif method == "HEAD":  # if the method is get
                try:
                    send(path, "HEAD")
                except FileNotFoundError:
                    error(404)
            else:
                error(405)
        elif os.path.isdir(path):  # if the dir is a dir
            sendir(path)
        else:
            # print("else")
            error(404)

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
