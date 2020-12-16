ACTF_client for Aggregate collective TCP flows client

## 环境说明
1. 开发系统：win10
1. 开发工具：Pycharm 2020.1
1. 开发语言：Python3.6

## 环境配置
```shell script
make init
```

## milestone
### 1. 2020-12-17
- 描述：完成两个客户端的分布式加法计算
- commit: `1972356c`
- run: 
```shell script
# 先启动服务端，进入服务端目录下，执行:
make run
# 再启动客户端，进入客户端目录下，执行:
make run
```

## 单元测试
```shell script
make unittest
```

