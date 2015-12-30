#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import socket
import json
import hashlib
from progressbar import *

class Client_Handler(object):
    response_code = {
            '200': "pass user authentication",
            '401': "wrong username or password",
            '404': "invalid username or password",
            '300': "Ready to send file",
            '301': "Ready to get file from server",
            '302': "Ready to send to  server",
            '303': "Ready to recv file from client",
            '403': "File doesn't exist on ftp server",
    }
    def __init__(self,args):
        self.args = args
        self.argv_parser() #调用判断参数的方法
        self.client_handel()
    def argv_parser(self):
        if len(self.args) == 1: #判断是否程序后跟了参数如果没有跟参数提示帮助信息
            self.help_msg()
        else:
            try:
                self.ftp_host = self.args[self.args.index('-s') +1] #获取程序后面-s 后的参数
                self.ftp_port = int(self.args[self.args.index('-p') +1]) #获取程序后面-p 后的参数
            except (IndexError,ValueError):
                self.help_msg()
                sys.exit()

    def help_msg(self):
        msg = '''
        example    :python client.py -s ip_address -p port_number
        -s         :which ip address you will connection
        -p         :which port you will connection
        help       :print help information
        '''
        sys.exit(msg)

    def connection(self,host,port): #定义连接函数
        try:
            print host,port
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #实例化socket
            self.sock.connect((host,port)) #连接socket服务器
        except socket.error as e:
            sys.exit("\033[31;1m%s\033[0m"%e)


    def auth(self): #定义认证函数
        try:
            retry_count = 0
            while retry_count < 3:
                username = raw_input("\033[32;1mPlease input user name:\033[0m")
                if len(username) == 0: continue #如果用户没有输入重新输入
                userpass = raw_input("\033[32;1mPlease input  password:\033[0m")
                if len(userpass) == 0: continue #如果用户密码没有输入重新输入
                hash = hashlib.md5()  #md5加密
                hash.update(userpass) #md5加密
                userpass = hash.hexdigest()#md5加密
                acount_info = json.dumps({
                    'username':username,
                    'password':userpass}) #把用户的输入转换成josn模式
                auth_string = "user_auth|%s" % (acount_info) #把动作和信息一起发送过去！
                self.sock.send(auth_string) #发送登录信息
                server_response = self.sock.recv(1024) #接收server端返回的状态信息
                print server_response
                response_codeid = self.get_response_code(server_response)
                print response_codeid
                print (self.response_code[response_codeid]) #获取上面定义的code状态
                if response_codeid == '200':
                    self.login_user = username
                    self.cwd = '/'
                    return True
                else:
                    retry_count += 1
            else:
                sys.exit('\033[31;1mToo many attempt\033[0m')
        except Exception as e:
            print e
    def get_response_code(self,code): #获取状态码函数
        response_info = code.split("|") #分割server端返回的状态信息
        print response_info
        codenow = response_info[1] #获取状态码所在字段
        return codenow #返回状态码
    def parse_instruction(self,user_input): #拼接函数
        user_input_to_list = user_input.split()  #把用户的输入用空格分割
        func_str = user_input_to_list[0] #获取元素
        if hasattr(self,'instruction__'+ func_str): #判断拼接后的方法是否存在
            return True,user_input_to_list #返回True并返用户输入
        else:
            return False,user_input_to_list #如果没有返回False，并返回输入
    def interactive(self):
        try:
            self.logout_flag = False
            while  self.logout_flag is not True:
                print """\033[34;1mget filename    :will to download file from server
push filename   :filename    will to update file to server
show    :will list server file and Directory list\033[0m
                """
                user_input = raw_input("[%s]:[%s]:" %(self.login_user,self.cwd)).strip() #获取用户输入
                if len(user_input) == 0:continue
                status,user_input_instructions = self.parse_instruction(user_input) #parse_instruction 防止和python自定义命令冲突，把命令进行自定义拼接
                if status is True:
                    func = getattr(self,"instruction__" + user_input_instructions[0]) #通过反射查找相应的方法
                    func(user_input_instructions)
                else:
                    print("\033[31;1mInvalid instruction!\033[0m")
        except KeyboardInterrupt as e:
            print "\033[31;1mThe Client will be exit!\033[0m"
    def instruction__get(self,instructions): #下载函数
        if len(instructions) == 1: #如果后面没有跟文件名退出
            print("Input the remote filename which you want to be downloaded!")
            return
        else:
            file_name = instructions[1]  #获取文件名
            raw_str = "file_get|%s" % (json.dumps(file_name))  #拼接用户指令
            self.sock.send(raw_str) #发送指令至服务器
            response_str,code,file_size,file_md5 = self.sock.recv(1024).split('|')
            if code == '300':
                self.sock.send("response|301")
                total_file_size = int(file_size) #取出文件大小
                received_size = 0
                local_file_obj = open(file_name,"wb") #打开文件
                pbar=self.p_bar() #实例化对象
                mean = total_file_size/100 #获取平均值
                while total_file_size != received_size: #循环接收文件
                    data = self.sock.recv(4096)
                    received_size += len(data)
                    local_file_obj.write(data)
                    mean2 = received_size/mean #获取进度
                    pbar.update(mean2) #更新进度
                    if mean2 == 100: #如果传输完成
                        pbar.update(100) #更新
                        pbar.finish() #完成
                    #print("recv size:", total_file_size,received_size)

                else:
                    print("\033[32;1m----file download finished-----\033[0m")
                    local_file_obj.close() #关闭文件
                    download_md5 = self.hashfile(file_name) #调用MD5函数获取MD5值
                    if download_md5 == file_md5: #判断MD5值是否相等
                        print "\033[32;1mMD5 is same!\033[0m"
                    else:
                        print "\031[31;1mMD5 is different"
            elif code == '403' : #文件不存在
                print(self.response_code[code])
    def instruction__show(self,show):
        self.sock.send('file_show|file_name')
        file_list = self.sock.recv(1024)
        file_list = json.loads(file_list)
        for i in file_list:
            print i

    def instruction__push(self,instructions): #下载函数
        if len(instructions) == 1: #如果后面没有跟文件名退出
            print("Input the  filename which you want to be update to server!")
            return
        else:
            file_name = instructions[1]  #获取文件名
            if os.path.exists(file_name):
                raw_str = "file_push|%s" % (json.dumps(file_name)) #拼接发送的请求
                self.sock.send(raw_str) #发送至server端
                if self.sock.recv(1024) == '303': #接收返回的状态码如果为303
                    print "\033[34;1mwill to send file to server\033[0m"
                    file_size = os.path.getsize(file_name) #判断文件是否存在
                    self.sock.send(str(file_size)) #发送文件大小
                    self.sock.recv(1024) #接收状态信息
                    f = open(file_name,'rb') #打开文件
                    t_start = time.time()
                    sent_size = 0
                    pbar=self.p_bar()
                    mean = file_size/100 #获取平均值
                    while file_size != sent_size: #当文件大小不等时执行
                        data = f.read(4096)
                        self.sock.send(data) #发送大小
                        sent_size += len(data) #计算发送总数
                        mean2 = sent_size/mean
                        pbar.update(mean2)
                        if mean2 == 100: #当为100的时候发送完成
                            pbar.update(100)
                            pbar.finish()

                        #print ("send:",file_size,sent_size)
                    else:
                        t_cost = time.time() - t_start
                        print "----file transfer time:---",t_cost
                        print("\033[32;1m----successfully sent file to server----\033[0m")

            else:
                print "\033[31;1mPlese input right file name !\033[0m"
    def hashfile(self,filename):  #定义md5认证函数
        md5 = hashlib.md5()
        with open(filename,'rb') as f: #打开文件
            while True:
                data = f.read(1024) #循环读取文件内容
                if not data:
                    break
                md5.update(data) #更新md5值
            return md5.hexdigest() #返回md5值
    def p_bar(self):
        #download可以自己修改，想了解其他的特性自己看源码吧
        widgets = ['Download: ', Percentage(), ' ', Bar(marker=RotatingMarker()),]
        pbar = ProgressBar(widgets=widgets, maxval=100).start()
        return pbar
    def client_handel(self): #
        self.connection(self.ftp_host,self.ftp_port) #调用连接方法
        if self.auth():#调用认证方法
            self.interactive()
