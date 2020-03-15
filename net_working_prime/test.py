import os, mimetypes
import urllib.request
import urllib.parse

stri = "称"
# sd = bytes(stri, encoding="utf-8")
# sff = str(sd, encoding="utf-8")

encodeStr = urllib.parse.quote(stri)
stt = bytes(stri, encoding="utf-8")
sgg = urllib.parse.unquote(encodeStr)
# sdd = urllib.parse.quote_from_bytes(stt)
# sdd = unicode()
print(sgg)

# current_path = os.path.dirname(__file__)
# print(os.getcwd())
# print(current_path)
# url = urllib.request.pathname2url("./test.py")
# print(mimetypes.guess_type(url)[0])
# print(os.listdir(".././"))
# print(os.path.getsize("./test.py"))
# file = open("aweb.py")
# print('\r\n'.join(b'aloha', b'b', b'c').encode())
# str = b'rr'
# seq = (b'b', b'jj')
# print(str.join(seq))
# status = "HTTP/1.0 200 OK"
# type = "Content-Type:text/html; charset=utf-8"
# conn = "Connection: close"
# line = b''
# h = "<html><body>Hello World!<body></html>"
# # "\r\n"
# stri = b'\r\n'
# seq = (str.encode(status) , str.encode(type),str.encode(conn),line,str.encode(h),line)
# print (stri.join(seq))