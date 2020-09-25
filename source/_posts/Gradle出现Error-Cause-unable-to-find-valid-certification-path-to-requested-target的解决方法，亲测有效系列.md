---
title: >-
  Andoir Gradle出现Error:Cause: unable to find valid certification path to requested
  target的解决方法，亲测有效系列
date: 2020-09-16 15:48:14
tags: Android
categories: Android
---
#### 前言（废话）
由于公司出现题述问题，导致严重影响本人学习Android，所以费劲心思终于找到了国内的镜像。

#### 解决方法
```
buildscript {
  repositories {
    maven { url 'http://maven.aliyun.com/nexus/content/repositories/google' }
    maven { url 'http://maven.aliyun.com/nexus/content/repositories/jcenter'}
  }
  dependencies {
    classpath 'com.android.tools.build:gradle:3.6.1'
    // NOTE: Do not place your application dependencies here; they belong
    // in the individual module build.gradle files
  }
}
allprojects {
  repositories {
//    google()
//    jcenter()
    maven { url 'http://maven.aliyun.com/nexus/content/repositories/google' }
    maven { url 'http://maven.aliyun.com/nexus/content/repositories/jcenter'}
  }
}
```
修改`build.gradle`为以上代码部分，即可同步阿里的源，一般家里第一次同步不要走代理，后续可以走，尽量等到同步完成。当然如果你要像这样同步阿里源还是飞快的。