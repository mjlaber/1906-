"""
    服务端 dict
    功能： 业务逻辑处理
    模型： Thread 多进程 tcp 并发
"""
import os
import signal
import sys
from socket import *
from threading import Thread
from time import sleep

from dict_db import DataBase

HOST = "0.0.0.0"
PORT = 2222
ADDR = (HOST,PORT)

# 数据库操作对象
db = DataBase()

# tcp多线程服务端
class TcpThreadServer(Thread):

    def __init__(self, connfd):
        super().__init__()
        self.connfd = connfd

    # 登录
    def do_login(self,data):
        tmp = data.split(" ")
        name = tmp[1]
        passwd = tmp[2]
        if db.register(name,passwd):
            self.connfd.send("登录成功".encode())
        else:
            self.connfd.send("登录失败".encode())

    # 注册
    def do_register(self,data):
        tmp = data.split(" ")
        name = tmp[1]
        passwd = tmp[2]
        if db.register(name,passwd):
            self.connfd.send(b"OK")
        else:
            self.connfd.send(b"Fail")
    # 查单词
    def do_query(self,data):
        tmp = data.split(" ")
        name = tmp[1]
        word = tmp[2]

        # 插入历史记录
        db.insert_history(name,word)

        # 通过数据库找到单词 (找到返回解释，找不到返回None）
        mean = db.query(word)
        if mean:
            msg = "%s : %s"%(word,mean)
            # self.connfd.send(b'word')
        else:
            # self.connfd.send("Fail".encode())
            msg = "没找到"
        self.connfd.send(msg.encode())
    # 历史记录
    def do_history(self,data):
        name = data.split(' ')[-1]
        r = db.read_history(name)
        for i in r:
            # i --> (name word time)
            msg = "%s %-16s  %s"%i
            sleep(0.1)
            self.connfd.send(msg.encode())
        sleep(0.1)
        self.connfd.send(b"##")

    # 接收请求
    def handle(self):
        """
        请求类型：
        E:退出  L：登录  R：注册  Q：查单词  H:查历史记录
        :return:
        """
        while True:
            data = self.connfd.recv(1024).decode()
            if not data or data == "E":
                self.connfd.close()
                # os._exit(0) # 退出服务器
                return        # 退出循环
            elif data[0] == "L":
                self.do_login(data)
            elif data[0] == "R":
                self.do_register(data)
            elif data[0] == "Q":
                self.do_query(data)
            elif data[0] == "H":
                self.do_history(data)
            else:
                self.connfd.send("命令错误!")

# 主函数 程序启动入口
def main():
    # 创建套接字
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    sockfd.bind(ADDR)
    signal.signal(signal.SIGCHLD,signal.SIG_IGN)
    sockfd.listen(5)
    print("Listen the port 2222...")
    # 循环等待客户端连接
    while True:
        try:
            connfd,addr = sockfd.accept()
        except KeyboardInterrupt:
            db.close() # 关闭数据库连接
            sys.exit()
        except Exception as e:
            print(e)
            continue
        print("Connect from ",addr)

        # 多线程处理
        ts = TcpThreadServer(connfd)
        ts.handle()
        ts.setDaemon(True)
        ts.start()

if __name__ == '__main__':
    main()

