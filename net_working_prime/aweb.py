import asyncio
import os
import urllib.request
import mimetypes
import urllib.parse


async def dispatch(reader, writer):
    data = await reader.read(2048)

    def send(path, meth):       # if the requested dir is a file, invoke this function
        url = urllib.request.pathname2url(path)     # get the type of the file
        mimety = mimetypes.guess_type(url)
        lent = os.path.getsize(path)                # get the length of the file
        status = "HTTP/1.0 200 OK"                  # the following are the response
        type = "Content-Type: " + str(mimety[0]) + "; charset=utf-8"
        length = "Content-Length: " + str(lent)
        conn = "Connection: close"
        line = b''
        stri = b'\r\n'
        if meth == "GET":           # if the method is get
            seq = (bytes(status, encoding="utf-8"), bytes(type, encoding="utf-8"), bytes(length, encoding="utf-8"), bytes(conn, encoding="utf-8"), line, line)
            writer.writelines(          # turn the response into bytes and write them
                [stri.join(seq)]
            )
            file = open(path, 'rb')         # open the file and write it
            writer.write(file.read())
        elif meth == "Head":        # if the method is head
            seq = (bytes(status, encoding="utf-8"), bytes(type, encoding="utf-8"), bytes(length, encoding="utf-8"), bytes(conn, encoding="utf-8"), line)
            writer.writelines(          # turn the response into bytes and write them
                [stri.join(seq)]
            )

    def sendir(path):           # if the requested dir is a dir, invoke this function
        status = "HTTP/1.0 200 OK"          # the following are the response
        type = "Content-Type:text/html; charset=utf-8"
        conn = "Connection: close"
        line = b''
        back = os.path.dirname(path)        # get the former dir
        h1 = "<html><head><title>Index of " + path + "</title></head>" \
             "<body bgcolor=\"white\">" \
             "<h1>Index of " + path + "</h1><hr>" \
             "<pre>"
        h2 = "<a href=\"" + back + "\">../</a><br>"
        h3 = "</pre>" \
             "<hr>" \
             "</body></html>"
        dirs = os.listdir(path)             # get the list of the dirs and files of the current dir
        for i in range(0, len(dirs)):       # add them to the html
            checkpath = path + "/" + dirs[i]
            if os.path.isfile(checkpath):
                h2 += "<a href=\"" + checkpath + "\">" + dirs[i] + "</a><br>"
            else:
                h2 += "<a href=\"" + checkpath + "\">" + dirs[i] + "/</a><br>"
        h = h1 + h2 + h3
        stri = b'\r\n'
        seq = (bytes(status, encoding="utf-8"), bytes(type, encoding="utf-8"), bytes(conn, encoding="utf-8"), line, bytes(h, encoding="utf-8"), line)
        writer.writelines(              # turn the response into bytes and write them
            [stri.join(seq)]
        )

    def error(sta):             # if error occurs, invoke this function
        status = ""
        if sta == 405:          # if it is a 405 error
            status = "HTTP/1.0 405 Method Not Allowed"
        elif sta == 404:        # if it is a 405 error
            status = "HTTP/1.0 404 Not Found"
        stri = b'\r\n'
        line = b''
        seq = (str.encode(status), line)
        writer.writelines(      # write the response
            [stri.join(seq)]
        )

    header_lines = str(data, encoding="utf-8").split('\r\n')            # turn data into string and split it
    path = ""
    # print(header_lines[0])
    if header_lines[0] != "":                               # split the first line to get the method, path and protocol
        method, path, protocol = header_lines[0].split(' ')
    if path == "/" or path == "":                           # return the dir of the current file
        path = os.getcwd()
    path = urllib.parse.unquote(path)                       # deal with Chinese characters
    # print(path)
    if os.path.isfile(path):                                # if the dir is a file
        if method == "GET":                                 # if the method is get
            try:
                send(path, "GET")
            except FileNotFoundError:                       # deal with error
                error(404)
        elif method == "HEAD":                              # if the method is get
            try:
                send(path, "HEAD")
            except FileNotFoundError:
                error(404)
        else:
            error(405)
    elif os.path.isdir(path):                               # if the dir is a dir
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
