---
title: Python工具函数
date: 2020-08-31 18:48:59
tags: python
categories:  python
---
```python 

def pb2jb(byte_arr):
    """
    python字节码转java字节码
    :param byte_arr:
    :return:
    """
    return [int(i) - 256 if int(i) > 127 else int(i) for i in byte_arr]


def jb2pb(byte_arr):
    """
    java 字节码转python字节码
    :return:
    """
    return [i + 256 if i < 0 else i for i in byte_arr]


def hex2jb(hex_str):
    """
    十六进制数据转java字节码
    eg:
        hex_str = "5f 3c f2 81 c8 0f 88 89 c7 b1 99 77 58 c5 4c 04"
    :return:
    """
    return [int(i, 16) - 256 if int(i, 16) > 127 else int(i, 16) for i in hex_str.split(" ")]


def hex2pb(hex_str):
    """
    十六进制数据转python字节码
    eg:
        hex_str = "5f 3c f2 81 c8 0f 88 89 c7 b1 99 77 58 c5 4c 04"
    :return:
    """
    return [int(i, 16) for i in hex_str.split(" ")]


def pb2str(byte_arr, encoding="utf-8"):
    """
    python字节码转str
    :return:
    """
    return bytes(byte_arr).decode(encoding)


def jb2str(byte_arr, encoding="utf-8"):
    """
    java字节码转str
    :return:
    """
    return bytes(jb2pb(byte_arr)).decode(encoding)


def hex2str(hex_str, encoding="utf-8"):
    """
    hex转str
    :param hex_str: "2c 22 70 61 79 63 68 65 63 6b 6d 6f 64 65 22 3a"
    :param encoding:
    :return:
    """
    return bytes(hex2pb(hex_str)).decode(encoding)

```