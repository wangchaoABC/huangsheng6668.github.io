---
title: python碰到的好用模块（持续更新）
date: 2020-09-19 16:59:52
tags: python
categories: python
---
#### jsonpath
该模块是用于**取层次深的字典里的值**用的。
具体用法实例：
```python
import jsonpath

d = {
    "error_code": 0,
    "stu_info": [
        {
            "id": 314,
            "name": "矿泉水",
            "sex": "男",
            "age": 18,
            "addr": "北京市昌平区",
            "grade": "摩羯座",
            "phone": "18317155663",
            "gold": 100,
            "cars": [
                {"car1": "bmw"},
                {"car2": "ben-z"},
            ]
        }
    ]

}
result=jsonpath.jsonpath(d,'$..car2') #模糊匹配
result=jsonpath.jsonpath(d,'$.stu_info') #取到stu_info这里的所有内容
result = jsonpath.jsonpath(d, '$.stu_info[0]') #取到stu_info里的第1个元素
result = jsonpath.jsonpath(d, '$.stu_info[0].id')  # 取到stu_info里的第1个元素中的id
print(result)
```

