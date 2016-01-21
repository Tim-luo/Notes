#!/usr/bin/env python
#-*- coding:utf-8 -*-
__author__ = 'luotianshuai'

import os
import sys
import json
import time
import redishelper

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #获取文件所在的顶级目录，方便加载其他的模块
sys.path.append(BASE_DIR) #加载环境变量

from config import settings

class MonitorClient(object):
    def __init__(self):
        self.r = redishelper.RedisHelper() #连接Redis
        self.ip = settings.ClientIP #设置客户端IP
        self.host_config = self.get_host_config() #执行get_host_config方法并把值赋予给host_config
    def start(self):
        self.handle()
    def get_host_config(self): #定义get_host_config方法
        config_key = "HostConfig::%s" % self.ip
        config_info = self.r.get(config_key) #获取监控参数
        if config_info: #判断是否可以获取到
            config_info = json.loads(config_info)
        return config_info
    def handle(self):#主运行方法
        if self.host_config:#判断host_config是否有值
            while True: #循环
                for servers,val in self.host_config.iterms():
                    if len(val) < 3:#确保第一次客户端启动时会运行所有插件
                        self.host_config[servers].append(0)
                    plugin_name,interval,last_run_time = val
                    if time.time() - last_run_time < interval:#判断当前时间是否小于监控间隔
                        next_run_time = interval - (time.time() - last_run_time )
                        print "Service [%s] next run time is in [%s] secs" % (servers,next_run_time)
                    else:
                        print "------will to run the [%s] again------" % servers
                        self.host_config[servers][2] = time.time()
                time.sleep(1)
        else:
            print "\033[31;1mYour config is None,please check Server config!!\033[0m"

