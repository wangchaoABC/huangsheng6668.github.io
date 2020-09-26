---
title: app的加壳与脱壳
date: 2020-09-22 19:55:59
tags: Android逆向
categories: Android逆向
---
##### 逆向分析APP的一散流程:
>1. 使用自动化检测工具检测apk是否加壳，或者借助一些反编译工具依靠经验推断是否加壳，
>2. 如果apk加壳，则需要首先对apk进行脱壳﹔(Fart、Youpk、Dex-Dump三种常用方案)
>3. 使用jeb、jadx , apktool等反编译工具对apk进行反编译;
>4. 先依据静态分析中得到的关键字符串、关键api调用等方法快速定位需要分析的关键函数和流程;
>5. 如果依据简单的字符串、关键api无法快速定位，则apk可能使用了字符串加密、反射调用等手段，此时可结合h o o k 、动态调试等
>6. 定位到关键函数后，再根据是java实现还是jni实现进一步分析，其中so中的函数逻辑分析难度较大下面通过几个实例来看下流程
>7. JNI分析到IDA当中，IDA搜索不到响应的函数则为动态注册，动态注册是在**JNI_Onload**当中注册的，这个时候我们可以搜一下**我们想要的目标字符串**，倘若进行了字符串加密（ollvm），则搜索不到。此时可以尝试**hook registerNative**、art相关的地址进行监控

##### JVM的类加载器包括3种:
1. Bootstrap ClassLoader（引导类加载器）
C/C++代码实现的加载器，用于加载指定的JDK的核心类库，比如java.lang.、java.uti.等这些系统类。Java虚拟机的启动就是通过Bootstrap，**该Classloader在java里无法获取**，**负责加载/lib下的类。**
2. Extensions ClassLoader（拓展类加载器）
Java中的实现类为ExtClassLoader，**提供了除了系统类之外的额外功能，可以在java里获取，负责加载/lib/ext下的类**。
3. Application ClassLoader（应用程序类加载器）
Java中的实现类为AppClassLoader，是与我们接触对多的类加载器，**开发人员写的代码默认就是由它来加载**，**ClassLoader.getSystemClassLoader返回的就是它。**

###### 自定义类加载器
通过继承java.lang.ClassLoader来实现自己的ClassLoader
![picture 5](http://img.juziss.cn/13c6dab609d4e87d63436656493e0a9ebe43add24f48712e003aa4fa2c363d21.png)  

##### 双亲委派
类加载器通过双亲委派（也叫向上委托）的方式来进行类的加载。

>双亲委派模式的工作原理的是;**如果一个类加载器收到了类加载请求，它并不会自己先去加载，而是把这个请求委托给父类的加载器去执行，如果父类加载器还存在其父类加载器，则进一步向上委托，依次递归，请求最终将到达顶层的启动类加载器，如果父类加载器可以完成类加载任务，就成功返回，倘若父类加载器无法完成此加载任务，子加载器才会尝试自己去加载**，这就是双亲委派模式，即每个儿子都不愿意干活，每次有活就丢给父亲去干，直到父亲说这件事我也干不了时，儿子自己想办法去完成，这个就是双亲委派。

###### 为什么采用双亲委派
1. **避免重复执行类加载器**， 如果类已经被加载了，则可以直接读取已经加载的Class。
2. 更加安全，**无法用自定义的类替代系统类，防止系统级API被篡改。**

当年我老师给我上课时，跟我说过，以前有个黑客通过替换java.lang.String成自己的String从而引发安全危机。所以通过双亲委派就杜绝了这种问题的发生。

##### 类加载的时机
1. 隐式加载
	类不由开发人员进行加载的。
	触发时机：
	1. 创建类的实例
	2. 访问类的静态变量（读写）
	3. 调用类的静态方法
	4. 使用反射方式强制创建某个类或接口对应的java.lang.Class对象
	5. 初始化某个类的子类
2. 显示加载（在反射的过程当中用的频率较高）
	1. 使用LoadClass()加载
	2. 使用forName()加载
	两者有所区别：

##### JVM当中加载类的流程

1. 装载:查找和导入Class文件
2. 链接:其中解析步骤是可以选择的
	- 检查:检查载入的class文件数据的正
确性
	- 准备:给类的静态变量分配存储空间
	- 解析:将符号引用转成直接引用
3. 初始化:即调用<clinit>函数，对静态变
量，静态代码块执行初始化工作(反编译过程当中，这些静态代码将变成clinit函数，该函数由编译器自动生成)

![picture 6](http://img.juziss.cn/b321ba088c4cfaf7c9d0e3a0a702f825d09840be7ddbfc4fad7ecaf21e691aab.png)  

##### Android系统当中的ClassLoader的继承关系

![picture 7](http://img.juziss.cn/257c3dafbfe6de697ee0bf6de7dae56da5aefea35aa27007d5f385a09e3fb14f.png)  

其中InMemoryDexClassLoader为Android8.0新引入的ClassLoader.

采用InMemoryDexClassLoader写加壳代码非常方便。

ClassLoader: 抽象类
BootClassLoader: 继承自ClassLoader，与JVM中的BootStrapClassLoader作用一样，**用于预加载系统级别的类**，采用单例模式，确保只需加载一次核心的类即可。由Java实现。
BaseDexClassLoader:该类非常关键。**对一个d
ex加载的过程当中，大部分的逻辑都在该ClassLoader当中实现**,其子类`InMemoryDexClassLoader、PathClassLoader、DexClassLoader`只是简单的继承了BaseDexClassLoader。
PathClassLoader: 当一个App从点击到第一个Activity呈现的过程当中，APP当中的类由PathClassLoader来加载。
SecureClassLoader继承自ClassLoader,主要加入权限方面的功能，加强了安全性，其子类URLClassLoader是用URL路径从jar文件中加载类和资源。
**InMemoryDexClassLoader: 在Android 8.0 引入的，在APP的加固当中使用最多的就是在InMemoryDexClassLoader当中进行。顾名思义，从内存当中直接加载dex**
PathClassLoader: 是Android默认使用的类加载器,四大组件Activity、Service等等都是在PathClassLoader当中进行加载。
DexClassLoader: 可以加载任意目录下的dex、jar、apk、zip文件，甚至可以从网络、SD卡当中加载，**也是目前实现插件化、热修复以及dex加壳的重点！**

##### Android的源码目录
art: 存放Android runtime的实现，以C++代码为主
bionic: Android的C库
libcore: ClassLoader的存放处，编译到手机时以jar包的形式呈现
framework: Android四大组件的管理处

tips: android的源码可以到aospxref.com和androidxref.com当中查看，aosp为国内镜像且以更新到android 10

##### Android ClassLoader源码解析
ClassLoader位于其他所有ClassLoader的根节点。其中一个关键的变量`parent`是用于**实现双亲委派**的关键。该参数在每个ClassLoader当中都有存在，**用于表示它的父节点是哪个ClassLoader**,对于Android的BootClassLoader来说，parent是空的。再看看parent是一个final类型的变量，意味着只能赋值一次。该变量是否重要，对于如何插件化加载dex，并且让dex当中的组件生效。

![picture 8](http://img.juziss.cn/4d2faf6239fc518c1445598577287e1b9ce65fa71d58a4508d7ed7c5ae5c04e8.png)  

BaseDexClassLoader源码：
![picture 9](http://img.juziss.cn/3f443c049798b9018fb6b6fccf6778343550780c59ab1d07c0fe2db76394e330.png)  

DexClassLoader源码:
![picture 11](http://img.juziss.cn/a597581e02451f29eb5c0136d20cd999281c165c80e3c06177419abcdc809f26.png)  

PathClassLoader源码:
![picture 12](http://img.juziss.cn/055dfba62b176e2301cee5d678a27eeb3c4da4fd9a37ef30ff089ea5686aadb2.png)  

InMemoryDexClassLoader源码:
![picture 13](http://img.juziss.cn/9f6546bf1abdad5459aa20c99fa090c1b0736fdb8ea21384ed8bc027c4ede71a.png)  

以上三个子类均继承自BaseDexClassLoader,且仅仅只有自己的构造函数。

##### 证明：BootClassLoader为根ClassLoader
通过Android Studio写一个程序：


##### frida与xpose对ClassLoader的加载
xpose: 需要加载ClassLoader才能进行操作
frida: 通过反射找到app所在的ClassLoader, 自动处理ClassLoader

##### 动态加载dex
之前我们有提到DexClassLoader 可以加载任意目录的dex、zip、jar、apk文件，所以我们需要得到一个DexClassLoader实例，先看看源码部分。
![picture 11](http://img.juziss.cn/a597581e02451f29eb5c0136d20cd999281c165c80e3c06177419abcdc809f26.png)  
第一个参数dexPath,即要加载的那4个类型的文件路径，第二个

1. 我们先创建一个Android项目，然后我们再创建一个类，类中创建一个方法，用来输出已经被调用到。

2. 编译整个项目成apk，然后解压apk，找到当前classxx.dex，把其导入到手机的/sdcard/目录

3. 接着，我们创建一个用于Load刚才我们导入进sdcard的项目，记得添加读写sd卡的权限.
![picture 1](http://img.juziss.cn/25119105b2a77f7811e8d7484daa360993d4b9f86e6d04e639db6a97a6d8b873.jpg)  

4. 编写程序
```java
package com.example.loadsdcardcode;

import androidx.appcompat.app.AppCompatActivity;

import android.app.Application;
import android.content.Context;
import android.os.Bundle;

import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

import dalvik.system.DexClassLoader;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Context context = this.getApplicationContext();
        testDexClassLoader(context, "/sdcard/3.dex");
    }

    /**
     *
     * @param context 获取当前app的私有目录
     * @param dexPath dex、zip、apk、jar这四种中的一种文件格式的路径
     */
    public void testDexClassLoader(Context context, String dexPath){
        // 在当前的私有文件下新建一个私有目录,用于存放其dex
        File optfile = context.getDir("opt_dex", 0);
        File libFile = context.getDir("lib_dex", 0);
        DexClassLoader dexClassLoader = new DexClassLoader(dexPath,
                optfile.getAbsolutePath(),
                libFile.getAbsolutePath(),
                MainActivity.class.getClassLoader());
        try {
            // 读取dex中的class
            Class clazz = dexClassLoader.loadClass("com.example.beloadedproject.TestClass");
            try {
                // 反射出需要的method
                Method method = clazz.getDeclaredMethod("functionBeLoaded");
                // 反射出我们要load的class
                Object obj = clazz.newInstance();
                // 调用方法
                method.invoke(obj);
            } catch (NoSuchMethodException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            } catch (InstantiationException e) {
                e.printStackTrace();
            } catch (InvocationTargetException e) {
                e.printStackTrace();
            }

        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }
    }
}
```
看看结果：
![picture 1](http://img.juziss.cn/02bd1331331a16fed90a1cbb54083152375b4224366b70f5744331242a980448.png)  


DexClassLoader方法参数:
dexPath:目标所在的apk或者jar文件的路径，装载器将从路径中寻找指定的目标类。
dexOutputDir:由于dex文件在APK或者jar文件中，所以在装载前面前先要从里面解压出dex文件，这个路径就是dex文件存放的路径，在android系统中，一个应用程序对应一个linux用户id ,应用程序只对自己的数据目录有写的权限，所以我们存放在这个路径中。
libPath:目标类中使用的C/C++库。
最后一个参数是该装载器的父装载器，一般为当前执行类的装载器。

##### APP运行的过程
![picture 2](http://img.juziss.cn/cc369254dbb9c7f913a109b608583dbb979e32b9fe79b03b4729eb508e7f2c95.png)  
ActivityThread.main()是进入APP世界的大门，只有经过这个方法之后才会进入到加壳app的自己的代码当中。
接下来我们开始讲ActivityThread:

##### ActivityThread
ActivityThread是一个单例模式的类，sActivityThread用于保留这个唯一的实例。
我们要想获取到当前的ActivityThread，需要调用其静态函数`currentActivityThread`
![picture 3](http://img.juziss.cn/76c59cbeb09ae923b8660b0d266301efdb0a1f9bf9dbb75141bff33d256d691b.png)  

通过该函数，我们将获取这个全局、单例的实例，通过该实例我们可以获取一些比较重要的变量。

LoadedApk:
![picture 6](http://img.juziss.cn/5ed455d389703908e896b02ec1689ff4d8bbde4a51c8c0f3c5888da5e9ae55bf.png)  


在ActivityThread的内部这个部分有LoadedApk这个类的变量，其中这个类中有一个变量叫做`mClassLoader`，就是我们加载APP用的ClassLoader，即PathClassLoader.

我们通过反射获取一个ActivityThread这个仅有的实例，接下来，再通过反射获取mPackages这个ArrayMap,接下来就可以通过当前APP的包名获取到它的LoadedApk,最后就可以通过这个LoadedApk获取到其中的一个mClassLoader。
![picture 7](http://img.juziss.cn/91efc5b43b9f48d9f9542bd19e97798385d697eacbe4df35c99f43cd28cac293.png)  

这个实际上就是PathClassLoader,就是接下来APP用于加载四大组件这些类的ClassLoader。

###### 而什么时候才会进入到app的代码当中？（何时进行dex解密）
在`handleBindApplication`当中，最先进入到app自身代码当中。
在hangbingle老师的这片文章[链接](https://bbs.pediy.com/thread-252630.htm, 'title')就有提到，此处上他的代码截取
```java
private void handleBindApplication(AppBindData data) {
    //step 1: 创建LoadedApk对象
    data.info = getPackageInfoNoCheck(data.appInfo, data.compatInfo);
    ...
    //step 2: 创建ContextImpl对象;
    final ContextImpl appContext = ContextImpl.createAppContext(this, data.info);
 
    //step 3: 创建Instrumentation
    mInstrumentation = new Instrumentation();
 
    //step 4: 创建Application对象;在makeApplication函数中调用了newApplication，在该函数中又调用了app.attach(context)，在attach函数中调用了Application.attachBaseContext函数
    Application app = data.info.makeApplication(data.restrictedBackupMode, null);
    mInitialApplication = app;
 
    //step 5: 安装providers
    List<ProviderInfo> providers = data.providers;
    installContentProviders(app, providers);
 
    //step 6: 执行Application.Create回调
    mInstrumentation.callApplicationOnCreate(app);
```
![picture 9](http://img.juziss.cn/538a0ba26e99f9d251177ca46b04e10fba73582ef02dd3c86ad4e41776ad3730.png)  

接下来我们看看那个newApplication做了什么。
![picture 10](http://img.juziss.cn/5f69e18eebe7a92cab70715dfd7e7420084fde248f0c3cae497c1e120efa808f.png)  

跟到这里发现app.attach,我们接着跟到attach里。
![picture 11](http://img.juziss.cn/d65d81ddbe0bd5f10ab3690320a142fc2069a2b0248edd9200d57cbe386dda6b.png)  

这里实际上调用了`attachBaseContext`这个函数。
一个正常的APP的哪一部分最先被执行？在AndroidManifest.xml当中，所声明的ApplicationBaseContext和onCreate函数是最先获取到执行权的。
在这个过程当中，涉及到两个ClassLoader,**BootClassLoader用来加载系统核心库，而PathClassLoader用于加载APP自身dex，其中包含有app所声明的Application,如果APP没有加壳，自然而然拥有APP这些类信息；如果加壳了呢？此时PathClassLoader加载的，只有壳的代码！**而且，当前呢，也还没有加载真正的代码也就是壳解密后释放的代码。**接下来就进入到Application的attachBaseContext这个函数执行，再往下就是onCreate函数进行执行。对于壳程序来说需要找到一个比较早的时机进行加密dex交付。自然而然就会选择这两个函数做文章。**
![picture 12](http://img.juziss.cn/9939bff51cfb9ddf3e37861d5852011490fe24a79ffe95c36581cc66be023b4e.png)  

###### 加壳应用的运行流程
![picture 13](http://img.juziss.cn/8149fa527dff3315f60320b038c2df1bbf0eeb36f8854d9e1083fca8fe52269c.png)  

###### 如何解决动态加载中加壳dex的类的生命周期