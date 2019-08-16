"""
    模拟网站的后端应用
    从httpserver接收具体请求
    根据请求进行逻辑处理和数据处理
    将需要的数据反馈给httpserver
"""
import json
import os,signal
from socket import *
from settings import *
from select import *
from urls import *


# 应用类，实现具体的后端功能
class Application:
    def __init__(self):
        self.host = frame_ip
        self.port = frame_port
        self.create_socket() # 创建套接字
        self.bind()          # 绑定地址
        self.fdmap = {}      # 查找地图
        self.signal = signal.signal(signal.SIGCHLD,signal.SIG_IGN)

    # 创建套接字
    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, DEBUG)

    # 绑定地址
    def bind(self):
        self.address = (self.host, self.port)
        self.sockfd.bind(self.address)


    # 用于服务启动
    def start(self):
        self.sockfd.listen(5)
        print("Listen the port %d"%self.port)
        self.fdmap[self.sockfd.fileno()] = self.sockfd # 查找地图
        self.ep = epoll() # 生成epoll对象
        # 关注sockfd
        self.ep.register(self.sockfd,EPOLLIN)
        while True:
            events = self.ep.poll()
            for fd,event in events:
                if fd == self.sockfd.fileno():
                    connfd,addr = self.fdmap[fd].accept()
                    self.ep.register(connfd)
                    self.fdmap[connfd.fileno()] = connfd
                else:
                    self.handle(self.fdmap[fd])
                    self.ep.unregister(fd)
                    del self.fdmap[fd]
    # 具体处理请求
    def handle(self,connfd):
        request = connfd.recv(4096).decode()
        request = json.loads(request)
        # request --> {'method':'GET','info':'/'}
        if request['method'] == 'GET':
            if request['info'] == '/' or request[-5:] == '.html':
                response = self.get_html(request['info'])
            else:
                response = self.get_data(request['info'])
        elif request['method'] == 'POST':
            pass

        # 将数据发送给Httpserver
        response = json.dumps(response)
        connfd.send(response.encode())
        connfd.close()

    # 网页处理函数
    def get_html(self,info):
        if info == '/':
            filename = STATIC_DIR + "index.html"
        else:
            filename = STATIC_DIR + info
        try:
            fd = open(filename)
        except:
            f = open(STATIC_DIR + '/404.html')
            return {'status':'404','data':f.read()}
        else:
            return {'status':'200','data':fd.read()}

    # 处理数据
    def get_data(self,info):
        for url,func in urls:
            if url == info:
                return {'status':'200','info':func}
        return {'status':'404','info':"Sorry..."}

if __name__ == '__main__':
    app = Application()
    app.start()