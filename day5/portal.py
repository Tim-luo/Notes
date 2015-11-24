#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pickle
import login

'''
商城接口
'''
#print login.login_api()

with open('user_info','rb') as f:
    usernew_info = pickle.load(f)
def wrapper(func):
    def inner():
        check_user = login.login_api()
        if check_user == "登录成功":
            func()
        else:
            return check_user
    return inner

@wrapper
def buy():
    print "\033[32;1m欢迎光临本商场，下面是本商场所包含的商品，请输入左侧的商品号购买:\033[0m"
    product_list = [
        ('Iphon',5800),
        ('Bike',800),
        ('Book',45),
        ('Coffee',35),
        ('iphon touch',1590),
        ('MX4',1999)
    ]
    shoping_list = []  #定义一个空列表，把用户选择的商品加入到空列表中（类似购物车）
    while True:
        index = 1  #定义索引值从1开始
        for item in product_list:  #循环商品列表
            print "\033[32;1m%s: %s\t%s\033[0m" %(index,item[0],item[1])  #打印商品列表
            index += 1

        user_choice = int(raw_input("\033[33;1m温馨提示:输入0推出购物\033[0m|\033[34;1m输入数列号购买物品，请问您需要购买什么物品：\033[0m ").strip()) #.strip()把空格取消
        if user_choice == 0:  #定义推出接口
            ask_exit = raw_input("\033[33;1m为了防止您的误操作如果退出请输入yes/YES,输入其他任意键返回购物列表:\033[0m")
            if ask_exit == "yes" or ask_exit == "YES":
                print "\033[34;1m下面是您本次的购物清单：\033[0m"
                for buy_list in shoping_list: #打印出此次购买列表
                    print "\033[34;1m%s \033[0m" % buy_list[0]  #打印shoping_list 用户购买列表
                sum_money = 0
                for buy_money in shoping_list:
                    sum_money += buy_money[1]  #计算消费总额
                print "\033[32;1m本次您总共消费金额为：%d \033[0m" % sum_money #打印总共消费了多少钱
                #print  "\033[32;1m欢迎下次光临\033[0m"
                break
            else:
                continue
        user_choice -= 1 #这里因为是从1开始的了所以需要-1 要不然下面输入索引的时候会有问题！
        if user_choice >= index:  #判断用户输入是否超出下标范围
            print "\033[33;1m您输入的序列号超出了范围,请重新输入\033[0m "
            continue
        user_add = product_list[user_choice]  #匹配用户选择商品
        shoping_list.append(product_list[user_choice]) #把用户输入的的商品加入到购物车
        print "\033[34;1m物品 %s 已购买并加入购物车\033[0m" % product_list[user_choice][0]  #打印添加值购物列表

'''
@wrapper
def card_login(card_id,card_password):
    while True:
        print  银行系统欢迎您:
输入1：取现
输入2：还款
输入3：显示未出账单详情
        raw_input()
'''