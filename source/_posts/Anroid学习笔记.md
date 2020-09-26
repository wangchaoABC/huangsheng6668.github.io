---
title: Anroid学习笔记
date: 2020-08-19 14:37:36
tags: Android
categories: Android
---

##### 课程里用到的Linux命令
telnet ip port:该命令用于检测该ip的这个端口是否已经开放。

curl ip.sb: 该命令用于查询本机当前IP是多少.

strace: 用于诊断和调试Linux用户空间syscall跟踪器，可以用来监控用户空间进程和内核的交互。简单来说就是看系统调用的整个过程。

lsof: 英文释义为list open files,是一个列出当前系统打开文件的工具

netstat -aple（或者用-tuulp） | grep procese_name: 用于查看某个进程其监听端口

du -h *:查看当前文件夹的每个文件的大小

scp /path/filename username@servername:/path   : 通过ssh发送文件

##### 系统调用
是指允许在**用户空间的程序**向操作系统内核请求需要更高权限允许的**服务**，系统调用提供用户程序与操作系统内核之间的接口。

##### Java的new File()写文件的原理

Java本质上调用了C/C++来完成。写完之后是一个**art.so**,之后调用安卓调用`bionic-c ` (kali是用`glibc`)封装的函数，bionic-c其实是调用了syscall到内核里去写文件

##### Android原生网络通信库

1. 1 HttpClient
1. 2 HttpURLConnection

HttpClient,**现在已经没有人在用了**。Android5时官方不再推荐其，Android6的SDK甚至直接去掉了，**Android9时，Android更是彻底取消了对Apache HTTPClient的支持,Android开发官方推荐用HttpUrlConnection。**
HttpUrlConnection, 虽然官方推荐，但是**也很少有人用**，跟python的urllib库一样，第三方库已经非常优秀了，所以多数人选择了第三方库。

##### Okhttp3
Okhttp是Square公司开源的网络请求框架，优秀到HttpUrlConnection的底层实现也是基于Okhttp。现在主流是okhttp3，由于okhttp3与okhttp4的api改动较大，所以它还是主流，较新版本都已经基于kotlin，okhttp3是目前最流行的android网络请求框架。

##### Retrofit2
一个基于okhttp框架的网络请求框架

##### Android-Async-Http
该库基于HttpClient,目前由于HttpClient的过时和作者不再更新，所以该库仅仅作为了解。

##### Volley
13年Google发布的一款基于HttpURLConnection的**异步网络请求框架**。特别适合*数据量小，通信频繁*的网络操作，有一定的使用量。

##### OkHttp3示例：
目标：搭建一个按钮，点击之后发送网络请求。

1. 先是创建一个activity，这里我们可以使用`main_activity.xml`，在里面注册一个Button,只需在LinearLayout里创建button标签就行了。
![picture 2](http://img.juziss.cn/e881232dfc3900364ac607a7a532481364dd6b60b6345b1b4b5efbeeb9f6aea8.png)  

2. 接着就是在MainActivity.java里面创建Button对象，设定点击事件

	![picture 3](http://img.juziss.cn/cab873f7da55fc669ac45b14dfa7b6075674301928a3e4e21a5cbaa661c8dbdd.png)  

3. 先是测试一下，事件是否可以运行。
![picture 4](http://img.juziss.cn/d0284f04f5e36f93fe808aa74ae3c823510c7cfc20f47018be807405f883a92a.png)  
能跑就行。

