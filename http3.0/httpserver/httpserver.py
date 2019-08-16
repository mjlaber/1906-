"""
httpserver 3.0
    获取http请求
    解析http请求
    将请求发送给WebFrame
    从WebFrame接收反馈数据
    将数据组织为Response格式发送给客户端
"""

from socket import *
from threading import Thread
import json,re
from config import * # 导入配置文件

# 负责和webframe 交互，socket客户端
def connect_frame(env):
    s = socket()
    try:
        s.connect((frame_ip,frame_port))
    except Exception as e:
        print(e)
        return

    # 将env 转换为json发送
    data = json.dumps(env)
    s.send(data.encode())
    #接收webframe反馈的数据
    data = s.recv(1024 ** 2 * 10).decode()
    return json.loads(data)

# httpserver功能
class HTTPServer:
    def __init__(self):
        self.host = HOST
        self.port = PORT
        self.create_socket()
        self.bind()

    # 创建套接字
    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,DEBUG)

    # 绑定地址
    def bind(self):
        self.address = (self.host,self.port)
        self.sockfd.bind(self.address)

    # 启动服务
    def serve_forever(self):
        self.sockfd.listen(5)
        print("Start the http server: %d"%self.port)
        while True:
            connfd,addr = self.sockfd.accept()
            client = Thread(target= self.handle,args= (connfd,))
            client.setDaemon(True)
            client.start()

    # 具体处理客户端请求
    def handle(self,connfd):
        requset = connfd.recv(4096).decode()
        # print(requset)
        pattern = "(?P<method>[A-Z]+)\s+(?P<info>/\S*)"
        try:
            env = re.match(pattern,requset).groupdict()
        except:
            connfd.close()
            return
        else:
            # data就是从webframe得到的数据
            data = connect_frame(env)
            # print(data)
            self.response(connfd,data)
    # 处理请求
    def response(self,connfd,data):
        # data --> {'status':"200","info":"xxx"}
        if data['status'] == "200":
            responseHeaders = "HTTP/1.1 200 OK\r\n"
            responseHeaders += "Connect-type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = data['data']

        elif data['status'] == "404":
            responseHeaders = "HTTP/1.1 404 Not Found\r\n"
            responseHeaders += "Connect-type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = data['data']
        elif data['status'] == "302":
            responseHeaders = "HTTP/1.1 302 Found\r\n"
            responseHeaders += "Connect-type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = data['data']

        # 将数据发送给浏览器
        data = responseHeaders + responseBody
        connfd.send(data.encode())





if __name__ == '__main__':
    httpd = HTTPServer()
    httpd.serve_forever()