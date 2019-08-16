"""

"""
import json
from socket import *

s = socket()
s.bind(("0.0.0.0",8080))
s.listen(5)
while True:
    c,addr = s.accept()
    data = c.recv(1024).decode()
    print(data)
    data = json.dumps({"status":200,"data":"xxxxxxxxxxx"})
    c.send(data.encode())