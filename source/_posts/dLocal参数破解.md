---
title: dLocal参数破解
date: 2020-08-07 14:04:33
tags: JS逆向
categories: JS逆向 
---
该网站大致界面如下，我们需要获取的数据是红框里的数据，其加载为ajax.
![picture 16](http://img.juziss.cn/feb8365e149c47641076e1276c41ae1f78c8fa0334f603d14788a5496fa7ded1.png)  


其参数为：

![picture 14](http://img.juziss.cn/9fd7065820dbad6b2c893ef90ae916a3dc31134c019dd54bb409453301dbb561.png)  

经过检测，其必要的参数为

![picture 15](http://img.juziss.cn/4fbc5f8afb50a67799ccc94ea55c54937d76d3e9d10d1812019d6d7dfc45979e.png)  


token为非必须，这个就好办多了，一看token就是一个加密，既然加密参数不重要，这个最重要的就是找到data的规律。参数分析好了，看看请求头。
![picture 13](http://img.juziss.cn/4fbc5f8afb50a67799ccc94ea55c54937d76d3e9d10d1812019d6d7dfc45979e.png)  


这里我把cookie注释掉后请求返回了一串js,看来除了data还要处理cookie，我再测测看哪个cookie值是必须的。
![picture 12](http://img.juziss.cn/db50c95b8382088ff9d3e460ed8e0cc56a8a74f9803ef6776c23f19be052f413.png)  

也就是说必须的cookie值是这个`rbzid`.
在看看不对的cookie返回的js

![picture 11](http://img.juziss.cn/f97481cd10b52ea4f8f3868d17f6fee164dd06cb672f00c4c9a1dda75e98349a.png)  


也就是说我们要破解这一串js。

先用fiddler看看那串cookie在那里被设置的。

![picture 9](http://img.juziss.cn/c2cf72b6d46bf12e434d25c974735a2fcc8f5fa691d13dca630ed9572d620fed.png) 
这里没有，结果这个加密的链接这里就有设置这个cookie


![picture 10](http://img.juziss.cn/b7885a6940f2b24da491fa6359b6f20fbe418aa7aa6f142fc125594562779da0.png)  

 


小目标又变了，变成如何生成这串url并发送请求。先看第一个请求返回的html

![picture 8](http://img.juziss.cn/0f55116b3e8c5a1d116a2fe7887c0e0a8ebe8e8b631d76afb1b2dab9a2cc9fba.png)  

看来不怎么多，搞得都不想写ast了。不过还是试试看。

把unicode转成字母

![picture 7](http://img.juziss.cn/28b9e4875844d86a59420ac1907f5456d07cf4491fa8925e31622f68bddd6215.png)  

像这种的如果是`StringLiteral`直接把它的extra删掉就好。但是这种是`RegExpLiteral`这种需要把它运行一遍获取到真正的值时替换原节点即可，后来我发现直接转的话跟下一个参数没有空格导致报错，能力不行，自己手动加空格。

![picture 6](http://img.juziss.cn/c338dbb67479f0c291ea1313e5ece5c16d8453a4d79833144163e87f522c620b.png)  

效果如上。

把16进制转成10进制

![picture 5](http://img.juziss.cn/07bc52af2954dfb5c861591b07f5e2a2f9041ccd2c8a072836359368ec061a3c.png)  


可以看到显示的是raw,而10进制则为上面的value，我们可以把extra删掉这样就能显示value了。

![picture 4](http://img.juziss.cn/0213f1abbcf8ec3cb849109f7ae5f757891d46e380755b68481c23ad5fe55fe1.png)  


效果如上。

呼，做不是程序解决的活真是体力活。后面终于弄好了，开始解决逻辑的东西了~
我们要考虑的是自执行的函数，TOSS这个对象就不要管了。
先解决这种`xxx.xx(number)`这种形式的代码。
我这里先解决`var h = T0SS;`这类多余代码。

这里可以采用`path.scope.rename(oldStr, NewStr)`这个方法，直接替换h为T0SS就可以解决了。

然后就出现了多余的代码`var T0SS = T0SS;`我们可以通过一系列判断之后通过`path.remove()`删除掉相应节点。

接下来进入正题，解决`xxx.xx(number)`这种形式的代码。
碰到这种我们肯定要有T0SS以及它的相应函数，所以这一片代码要扣过来。这部分不讲了，直接上代码。

![picture 2](http://img.juziss.cn/1cf7aa7dd9031a2cea0040782dd2f582b6ba0842faff9c389fa92ac5b648fe1e.png)  

执行完以上的AST我们的待破解的代码就清晰很多了，这时候就需要补环境了。缺啥补啥，需要注意的是最后一行它的window.rbzns里的参数是动态的，所以我们也要考虑改成动态的。比如说碰到document.createElement这些。看看它的代码之间的关联，如果只是为HTML创建标签的话，直接删掉就好了。

![picture 1](http://img.juziss.cn/4b42540e94976501c175ad2b33fdfafe1fc5437d82a64a08b55767e8b6b8bfbc.png)  

可以考虑像我这样写，这样就会成动态的了。本篇只是在记录自己工作上碰到的一个网站，感觉用AST合适就记录下来了。大家可以练练手哦~
