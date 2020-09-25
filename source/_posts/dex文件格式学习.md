---
title: dex文件格式学习
date: 2020-09-11 09:48:18
tags: Android
categories: Android
---

##### 什么是dex
dex是Android系统特有的可执行文件，具有应用的全部指令及运行时数据。
.class通过dx工具整合到一个dex,使得各个类都能互相通信，且减小占用的空间，使得结构更加紧凑。

class文件和dex的结构存在本质上的不同。
![picture 1](http://img.juziss.cn/d13673ab9c3f5b6bcead86c3976035b039cedd31e68754afdc2fa5285e4d1592.png)  

