"""
    dict 客户端
功能: 根据用户输入,发送请求,得到结果
结构: 一级界面 --> 注册,登录,退出
     二级界面 --> 查单词,历史记录 注销
请求类型： 注册R 登录L 查单词Q 历史记录H 退出E
"""
import os
import sys
from socket import *
from threading import Thread
from getpass import getpass

HOST = "127.0.0.1"
PORT = 2222
ADDR = (HOST,PORT)

# tcp多线程客户端
class TcpThreadClient(Thread):
    def __init__(self, sockfd):
        super().__init__()
        self.sockfd = sockfd

    # 注册用户
    def register(self):
        while True:
            name = input("Name: ")
            # passwd = getpass("Password: ")
            passwd = input("Password: ")
            #passwd1 = getpass("Again: ")
            passwd1 = input("Again: ")
            if passwd != passwd1:
                print("两次密码不一致")
                continue
            if (' ' in name) or (' ' in passwd):
                print("不能输入空格")
                continue
            return self.register_issuccess(name, passwd)
    # 判断注册是否成功
    def register_issuccess(self, name, passwd):
        # msg = "R " + name + passwd
        msg = "R %s %s" % (name, passwd)
        self.sockfd.send(msg.encode())
        # 等待接收服务端反馈
        data = self.sockfd.recv(128).decode()
        print(data)
        if data == "OK":
            print("注册成功!")
            self.query(name)
        else:
            print("注册失败!")
        return

    # 登录
    def login(self):
        while True:
            name = input("User: ")
            # passwd = getpass("Passwd: ")
            passwd = input("Passwd: ")
            # msg = "L " + name + ' ' + passwd
            msg = "L %s %s"%(name,passwd)
            self.sockfd.send(msg.encode())
            data = self.sockfd.recv(1024).decode()
            if data == "登录成功":
                print(data)
                self.query(name)
            else:
                print(data)
                continue
    # 退出
    def quit(self):
        self.sockfd.send(b"E")
        sys.exit("谢谢使用！")

    # 一级界面 --> 登录界面
    def handle(self):
        while True:
            print("""
            ==================Welcome===============
                    1. 注册    2. 登录    3. 退出
            ========================================
            """)
            cmd = input("请输入选项: ")
            if cmd == "1":
                self.register()
            elif cmd == "2":
                self.login()
            elif cmd == "3":
                self.quit()
            else:
                print("请输入正确命令")

    # 查单词
    def do_query(self,name):
        while True:
            word = input("Word: ")
            if not word:
                # return
                break
            msg = "Q %s %s"%(name,word)
            self.sockfd.send(msg.encode())
            data = self.sockfd.recv(1024).decode()
            if not data or data == "Fail":
                print("查询失败")
                continue
            print(data)
    # 查历史记录
    def do_hist(self,name):
        msg = "H " + name
        # msg = "H "
        self.sockfd.send(msg.encode())
        while True:
            data = self.sockfd.recv(1024).decode()
            if data == "##":
                break
            print(data)


    # 二级界面 查单词
    def query(self,name):
        while True:
            print("""
                   ================Welcome=================
                        11. 查单词    22. 历史记录   33. 退出
                   ========================================
                   """)
            cmd = input("请输入选项: ")
            if cmd == "11":
                self.do_query(name)
            elif cmd == "22":
                self.do_hist(name)
            elif cmd == "33":
                return
            else:
                print("重新输入选项")

# 主函数 启动函数
def main():
    sockfd = socket()
    sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    try:
        sockfd.connect(ADDR)
    except Exception as e:
        print(e)
        os._exit(0)
    tc = TcpThreadClient(sockfd)
    tc.handle()
    # while True:
    #     print("""
    #     ================Welcome=================
    #             1. 注册    2. 登录   3. 退出
    #     ========================================
    #     """)
    #     cmd = input("命令: ")
    #     if cmd == "1":
    #         tc.register()
    #     elif cmd == "2":
    #         tc.login()
    #     elif cmd == "3":
    #         quit()

    # 多线程处理
    tc.setDaemon(True)
    tc.start()

if __name__ == '__main__':
    main()