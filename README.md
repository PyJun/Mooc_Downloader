### 				基于Python 爬虫的慕课视频下载【开源代码停止维护，软件仍在维护更新】

##### 1.  项目简介：

- 项目环境为 Windows10,  Python3
- 用 Python3.6 urllib3 模块爬虫，涉及模块包括标准库、三方库和其它开源组件，已打包成exe文件
- 支持Mooc视频，字幕，课件下载，课程以目录树形式下载到硬盘，支持Potplayer播放
- 支持中国大学，网易云课堂，有道精品课，有道领世，腾讯课堂，中公网校，新东方，学浪，抖音课堂，B站课堂，高途课堂，途途课堂，千聊，兴趣岛，橙啦，爱课程，学堂在线，慕课网，超星学习通（学银在线），智慧树，智慧职教，二十大慕课网课的视频课程下载，核心下载调用 Aria2c
- 用户可以直接下载 Release 下的 [学无止下载器](https://github.com/PyJun/Mooc_Downloader/releases)  安装即可使用
- 有关下载器的使用以及相关问题，点击查看[Mooc下载器帮助文档](https://github.com/PyJun/Mooc_Downloader/wiki)

##### 2. 功能演示：

![demo1.png](http://xuewuzhi.cn/images/demo1.png)

![demo2.png](http://xuewuzhi.cn/images/demo2.png)

##### 4.项目文件

- Mooc_Main.py	          整个项目的主程序,  其实是调用了 Mooc_Interface
- Mooc_Interface.py       人机交互接口模块
- Mooc_Config.py            Mooc 的配置文件
- Mooc_Base.py               Mooc  抽象基类
- Mooc_Potplayer.py       用于生成专用于 Potplayer 播放的 dpl 文件 
- Mooc_Request.py          用 urllib 包装的一个Mooc请求库
- Mooc_Download.py      调用 Aira2c 下载的命令接口
- Icourses                          有关爱课程的模块包
  - Icourse_Base.py              爱课程下载器的基类，继承自 Mooc_Base
  - Icourse_Config.py            配置文件
  - Icourse_Cuoc.py              爱课程视频公开课的下载的子类，http://www.icourses.cn/cuoc/
  - Icourse_Mooc.py             爱课程资源共享课的下载的子类，http://www.icourses.cn/mooc/

- Icourse163                      有关中国大学慕课的模块包
  - Icourse163_Base.py         中国大学慕课下载器的基类，继承自 Mooc_Base
  - Icourse163_Config.py       配置文件
  - Icourse163_Mooc.py        中国大学慕课下载器得子类，继承自 Icourse163_Base.py

##### 5.运行项目

请确保在项目工程的根目录下，然后在终端输入以下指令（python3 环境，无依赖的第三方模块）

```powershell
python -m Mooc
```

##### 6.打包指令

1. 首先确保已经安装 **pyinstaller**，若未安装，则用 pip 安装，打开终端，输入：

   ```powershell
   pip install pyinstaller
   ```

2. 然后在项目工程的根目录下，终端输入：

   ```powershell
   pyinstaller Mooc.spec
   ```

3. 最后会在项目工程根目录下出现一个**dist**文件夹，该文件夹会出现一个**Mooc-3.4.0.exe**程序

![package.png](http://xuewuzhi.cn/images/package.png)


##### 7.注意事项
项目代码已好久未更新，Releases下有我打包好的exe文件，可直接下载使用~
【该项目为早期开源的代码，最新版本代码未开源】
1. 新版代码涉及网站爬虫、解析、解密，开源后容易和谐失效
2. 新版本涉及太多的模块依赖（包括且不限于nodejs,electron,ariac2,annie,ffmpeg,wkhtmltopdf和一些自编译的python依赖库），难以分离出可独立可用的开源版
3. 实在没有精力同时维护二个开源和闭源版本的代码
4. 该项目并非完整的开源项目，提供的软件无病毒，可免费使用（也包含付费功能）
