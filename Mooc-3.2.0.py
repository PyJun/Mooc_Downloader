
'''
慕课视频下载器
'''

import sys
import os
import re
import json
from time import perf_counter as clock
from socket import timeout, setdefaulttimeout
from urllib import request 
from urllib import parse
from urllib.error import ContentTooShortError, URLError, HTTPError

__QQgroup__ = "196020837"
__email__  = "py.jun@qq.com  ze.ga@qq.com"
CODE = 'Mooc.jpg'   #  支付宝二维码领红包的图片
PLAYLIST = '播放列表.dpl'
PATH = os.path.dirname(os.path.abspath(__file__))  # 程序当前路径
TIMEOUT = 20  # 请求超时时间为 20 秒
setdefaulttimeout(TIMEOUT)
winre = re.compile(r'[?*|<>:"/\\\r\n\t\b\v\f\s]')  # windoes 文件非法字符匹配
start_time = clock()
start_size = 0
speed = 0

class Mooc:
    class MoocException(Exception):
        pass
    def __init__(self):
        self.mooc_url = 'http://tools.antlm.com/index.php'
        self.search_url = 'https://www.icourse163.org/dwr/call/plaincall/MocSearchBean.searchMocCourse.dwr'
        self.infos_url = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getMocTermDto.dwr'
        self.parse_url = 'https://www.icourse163.org/dwr/call/plaincall/CourseBean.getLessonUnitLearnVo.dwr'
        self.course_data = {'a':'ajax_query','course_url': None}
        self.search_data = {
            'callCount':'1',
            'scriptSessionId':'${scriptSessionId}190',
            'c0-scriptName':'MocSearchBean',
            'c0-methodName':'searchMocCourse',
            'c0-id':'0',
            'c0-e1':None,
            'c0-e2':'number:1',
            'c0-e3':'boolean:true',
            'c0-e4':'null:null',
            'c0-e5':'number:0',
            'c0-e6':'number:30',
            'c0-e7':'number:20',
            'c0-param0':'''Object_Object:{
                keyword:reference:c0-e1,
                pageIndex:reference:c0-e2,
                highlight:reference:c0-e3,
                categoryId:reference:c0-e4,
                orderBy:reference:c0-e5,
                stats:reference:c0-e6,
                pageSize:reference:c0-e7
                }''',
            'batchId':'1543633161622',
        }
        self.infos_data = {
            'callCount':'1', 
            'scriptSessionId':'${scriptSessionId}190', 
            'c0-scriptName':'CourseBean',
            'c0-methodName':'getMocTermDto', 
            'c0-id':'0', 
            'c0-param0':None,  # 'number:'+self.term_id,
            'c0-param1':'number:0', 
            'c0-param2':'boolean:true', 
            'batchId':'1543633161622'
        }
        self.parse_data = {
            'callCount': '1', 
            'scriptSessionId': '${scriptSessionId}190',
            'c0-scriptName':'CourseBean',
            'c0-methodName':'getLessonUnitLearnVo', 
            'httpSessionId':'5531d06316b34b9486a6891710115ebc',
            'c0-id': '0', 
            'c0-param0':None, #'number:'+meta[0],
            'c0-param1':None, #'number:'+meta[1], 
            'c0-param2':'number:0',
            'c0-param3':None, #'number:'+meta[2], 
            'batchId': '1543633161622'
        }
        self.count = 0  # 计数器
        self.rootDir = None # 下载课程的根目录
        self.term_id = None # 下载课程的标题 ID
        self.title = None  # 下载课程的标题
        self.infos = {}  # 课程视频和文件的链接请求信息，包含id等
        self.content = {}  # 课程视频链接内容

    def searchMooc(self, courseName):  # 通过课程名来查找慕课
        self.search_data['c0-e1'] = courseName
        data = parse.urlencode(self.search_data).encode('utf8')
        req = request.Request(url=self.search_url, data=data, method='POST')
        response = request.urlopen(req, timeout=TIMEOUT)
        text = response.read().decode('utf8')
        names = re.findall(r'highlightName="(.*?)"', text)  # 一些麻烦的正则匹配和筛选
        names = map(lambda s:re.sub(r'[{}# ]', '', s), names)
        names = map(lambda s:s.encode('utf8').decode('unicode_escape'), names)
        schools = re.findall(r'highlightUniversity="(.*?)"', text)
        schools = map(lambda s:re.sub(r'[{}# ]', '', s), schools)
        schools = map(lambda s:s.encode('utf8').decode('unicode_escape'), schools)
        urls = re.findall(r'courseId=(\d*);', text)
        urls = map(lambda s: "https://www.icourse163.org/course/WHUT-"+s, urls)
        courses = [{'name':na,'school':sch,'url':url} for na,sch,url in zip(names,schools,urls)]
        return courses

    def getSummary(self, course_url):
        """从课程主页面获取信息"""
        url = course_url.replace('learn', 'course')
        response = request.urlopen(url, timeout=TIMEOUT)
        text = response.read().decode('utf8')
        term_id = re.search(r'termId : "(\d+)"', text).group(1)
        names = re.findall(r'name:"(.+)"', text)
        title = '__'.join(names)
        self.title = winre.sub('', title) # 用于除去win文件非法字符
        self.term_id = term_id
        return self.title

    def getInfos(self):
        self.infos_data['c0-param0'] = 'number:'+self.term_id
        data = parse.urlencode(self.infos_data).encode('utf8')
        req = request.Request(url=self.infos_url, data=data, method='POST')
        response = request.urlopen(req, timeout=TIMEOUT)
        text = response.read().decode('unicode_escape')
        self.infos = {}
        chapters = re.findall(r'homeworks=\w+;.+?id=(\d+).+?name="((.|\n)+?)";',text)
        for i,chapter in enumerate(chapters,1):
            chapter_title = winre.sub('', '{'+str(i)+'}--'+chapter[1])
            self.infos[chapter_title] = {}
            lessons = re.findall(r'chapterId=' + chapter[0] + r'.+?contentType=1.+?id=(\d+).+?name="(.+?)".+?test', text)
            for j,lesson in enumerate(lessons,1):
                lesson_title = winre.sub('', '('+str(j)+')--'+lesson[1])
                self.infos[chapter_title][lesson_title] = {}
                subs = re.findall(r'contentId=(\d+).+contentType=(1).+id=(\d+).+lessonId=' +
                                    lesson[0] + r'.+name="(.+)"', text)
                pdfs = re.findall(r'contentId=(\d+).+contentType=(3).+id=(\d+).+lessonId=' +
                                lesson[0] + r'.+name="(.+)"', text)
                self.infos[chapter_title][lesson_title]['subs'] = {i:sub for i,sub in enumerate(subs,1)}
                self.infos[chapter_title][lesson_title]['pdfs'] = {i:pdf for i,pdf in enumerate(pdfs,1)}

    def getContent(self, course_url):  # 获取指定慕课URL的课程视频和课件链接，最后保存为字典
        self.course_data['course_url'] = course_url
        params = '?' + ''.join(k+'='+self.course_data[k]+'&' for k in self.course_data)
        response = request.urlopen(self.mooc_url+params, timeout=TIMEOUT)
        content = json.loads(response.read().decode('utf8'))['data']
        self.content = {}
        for i,chapter in enumerate(content,1):  # 去除 win 文价夹中的非法字符
            chapter_title = winre.sub('', '{'+str(i)+'}--'+chapter['chapter_title'])
            self.content[chapter_title] = {}
            j = 0
            for lesson in chapter:
                if lesson=='chapter_title': continue
                j += 1
                lesson_title = winre.sub('', '('+str(j)+')--'+chapter[lesson]['lesson_title'])
                self.content[chapter_title][lesson_title] = []
                for unit in chapter[lesson]:
                    if unit == 'lesson_title': continue
                    self.content[chapter_title][lesson_title].append(chapter[lesson][unit])

    def getSize(self, course_url):  # 获取待下载视频的大小
        cnt = 0
        while cnt < 10:
            try:
                response = request.urlopen(course_url, timeout=TIMEOUT)
                header =  dict(response.getheaders())
                size = float(header['Content-Length']) / (1024*1024)
                return size
            except URLError:
                cnt += 1
        raise Mooc.MoocException("资源异常")

    def download_sub(self, sub, lessonDir, name):
        self.parse_data['c0-param0'] = sub[0]
        self.parse_data['c0-param1'] = sub[1]
        self.parse_data['c0-param3'] = sub[2]
        data = parse.urlencode(self.parse_data).encode('utf8')
        req = request.Request(url=self.parse_url, data=data, method='POST')
        response = request.urlopen(req, timeout=TIMEOUT)
        text = response.read().decode('unicode_escape')
        subtitles = re.findall(r'name="(.+)";.*url="(.*?)"', text)
        for subtitle in subtitles:
            if len(subtitles) == 1:
                sub_name = name.strip('.srt')
            else:
                subtitle_lang = subtitle[0].encode('utf_8').decode('unicode_escape')
                sub_name = name.strip('.srt') + '_' + subtitle_lang
            sub_name = winre.sub('', sub_name)
            sub_path = os.path.join(lessonDir, sub_name)
            sub_url = subtitle[1]
            if not os.path.exists(sub_path+'.srt'):
                try:
                    downlaod_file(sub_url, sub_path+'.srt.pyjun')
                    os.rename(sub_path+'.srt.pyjun', sub_path+'.srt')
                except Mooc.MoocException:
                    pass

    def download_pdf(self, pdf, lessonDir, name):
        self.parse_data['c0-param0'] = pdf[0]
        self.parse_data['c0-param1'] = pdf[1]
        self.parse_data['c0-param3'] = pdf[2]
        data = parse.urlencode(self.parse_data).encode('utf8')
        req = request.Request(url=self.parse_url, data=data, method='POST')
        response = request.urlopen(req, timeout=TIMEOUT)
        text = response.read().decode('unicode_escape')
        pdf_url = re.search(r'textOrigUrl:"(.*?)"', text).group(1)
        pdf_name = winre.sub('', name.strip('.pdf'))
        pdf_path = os.path.join(lessonDir, pdf_name)
        if not os.path.exists(pdf_path+'.pdf'):
            try:
                downlaod_file(pdf_url, pdf_path+'.pdf.pyjun')
                os.rename(pdf_path+'.pdf.pyjun', pdf_path+'.pdf')
            except Mooc.MoocException:
                pass

    def download_video(self, source, lessonDir, isShd=True):  # 下载每个课程
        video_url = None
        hds = ('shdUrl', 'hdUrl') if isShd else ('hdUrl', 'shdUrl')
        for url_name in hds:  # 优先获取高清视频资源
            if not video_url:
                video_url = source.get(url_name,None)
        if video_url:
            self.count += 1
            unit = winre.sub('', '['+str(self.count)+']--'+source['unit_title'])
            video_name = unit.rstrip('.mp4')
            video_path = os.path.join(lessonDir, video_name) # 视频路径
            if not os.path.exists(video_path+'.mp4'):
                try:
                    size = self.getSize(video_url)
                    print("  |-{}    大小: {:.2f}M".format(align(video_name,50), size))
                    downlaod_file(video_url, video_path+'.mp4.pyjun', schedule) #下载文件，这里下载的是高清资源\
                    os.rename(video_path+'.mp4.pyjun', video_path+'.mp4')
                except Mooc.MoocException:
                    print("  |-{}    资源无法下载！".format(align(video_name,50)))
            else:
                print("  |-{}    已经成功下载！".format(align(video_name,50)))
            return video_path+'.mp4'
        return None

    def download(self, isShd=True):  # 根据课程视频链接来下载高清MP4慕课视频, 成功下载完毕返回 True
        print('\n{:^60s}'.format(self.title))
        if len(self.content) == 0:
            return None
        self.rootDir = os.path.join(PATH, self.title)
        if not os.path.exists(self.rootDir):
            os.mkdir(self.rootDir)
        listpath = os.path.join(self.rootDir, PLAYLIST)
        lines = []
        try:
            cnt = 0
            lines.append('DAUMPLAYLIST\n')
            for i,chapter in enumerate(self.content,1):  # 去除 win 文价夹中的非法字符
                print(chapter)
                chapterDir = os.path.join(self.rootDir, chapter)
                if not os.path.exists(chapterDir):
                    os.mkdir(chapterDir)
                for j,lesson in enumerate(self.content[chapter],1):
                    lessonDir = os.path.join(chapterDir, lesson)
                    if not os.path.exists(lessonDir):
                        os.mkdir(lessonDir)
                    print("  "+lesson)
                    self.count = 0
                    for count,source in enumerate(self.content[chapter][lesson],1):
                        video_path = self.download_video(source, lessonDir, isShd)
                        if video_path:
                            sub = self.infos[chapter][lesson]['subs'].get(self.count,None)
                            if sub:
                                self.download_sub(sub, lessonDir, winre.sub('', '['+str(self.count)+']--'+sub[3]))
                            cnt += 1
                            if cnt==1:
                                lines.append("playname=%s\n"%(video_path))
                            video_title = "(%d.%d.%d)--"%(i,j,self.count)+source['unit_title'].rstrip()
                            lines.append("%d*file*%s\n"%(cnt,video_path))
                            lines.append("%d*title*%s\n"%(cnt,video_title))
                            with open(listpath, 'w', encoding='utf8') as listfile:
                                listfile.writelines(lines)
                        sub = self.infos[chapter][lesson]['subs'].get(self.count,None)
                        pdf = self.infos[chapter][lesson]['pdfs'].get(count,None)
                        if pdf:
                            self.download_pdf(pdf, lessonDir, winre.sub('', pdf[3]))
            return True
        except (KeyboardInterrupt, Exception) as err:
            if isinstance(err, KeyboardInterrupt):  # 如果是用户自己中断 
                print()
            else:                                   # 否则即使网络问题
                print("\n请检查网络状态是否良好...") 
            return False

def downlaod_file(url, filename, backfunc=None):  # 用于处理网络状态不好时，重新下载
    global start_time, start_size, speed            # 若三次后还是无法下载，则报错
    cnt = 0 
    while cnt < 10:
        try:
            start_time = clock()  #  初始化时间，大小和速度
            speed = start_size = 0
            request.urlretrieve(url, filename, backfunc)
            return
        except (ContentTooShortError, URLError, ConnectionResetError, timeout):
            cnt += 1
        finally:
            request.urlcleanup()
    raise Mooc.MoocException("资源异常")

def schedule(a, b, c):  #下载进度指示 a:已经下载的数据块  b:数据块的大小 c:远程文件的大小
    global start_time, start_size, speed
    length = 66
    sch = min(100 * a * b / c, 100)
    per = min( length * a * b // c, length)
    if a%5 == 0 or per == length:
        if per <= length:
            print('\r  |-['+per*'*'+(length-per)*'.'+']  {:.2f}%  {:.2f}M/s'.format(sch,speed),end='  (ctrl+c中断)')
            if clock()-start_time > 0.5:  # 时间差大于0.5秒的时候刷新平均速度
                speed = (a*b-start_size) / ((clock()-start_time)*1024*1024)
                start_size = a*b
                start_time = clock()
        if per == length:
            print()

def align(string, width):  #  对齐汉字字符窜，同时截断多余输出
    res = ""
    size = 0
    for ch in string:
        if (size+3 > width):
            break
        size += 1 if ord(ch) <= 127 else 2
        res += ch
    res += (width-size)*' '
    return res

def get_SourceFile(filename):  # 获取打包后资源文件的位置，这里为二维码图片的路径
    if getattr(sys, 'frozen', False): #是否打包
        file_path = sys._MEIPASS
    else:
        file_path = PATH
    return os.path.join(file_path, filename)

def choice_hd():
    print("输入下载视频的清晰度(1:高清, 2:标清): ", end='')
    while True:
        try:
            num = int(input())
            if num not in (1, 2):
                print("请输入数字1或2: ", end='')
                continue
            return True if num==1 else False
        except ValueError:
            print("请输入数字1或2: ", end='')

def UI_interface(mooc):
    try:
        while True:
            os.system("cls")
            print("\t"+"="*91)
            print('\t|\t\t\t中国大学视频下载器 \t\tQQ群: {:^27s} |'.format(__QQgroup__))
            print("\t|\t\t\twww.icourse163.org\t\t邮箱: {:^27s} |".format(__email__))
            print("\t"+"="*91)
            print("\t\t\t博客: https://blog.csdn.net/qq_16166591/article/details/85249743")
            print("{:^100}".format("下载路径: "+PATH))
            keystr = input('\n输入一个视频课程网址或者一个课程名(q退出): ')
            while not keystr:
                keystr = input('\n输入一个视频课程网址或者一个课程名(q退出): ')
            if keystr == 'q':
                break
            match = re.search(r'(www.icourse163.org/.*?)(#/.*)?$', keystr)
            if match:
                course_url = "https://"+match.group(1)
            else:
                print("正在搜索课程......")
                try:
                    courses = mooc.searchMooc(keystr)
                except (URLError, ConnectionResetError, timeout):
                    input("请检查网络后继续...")
                    continue
                if courses == []:
                    print('很抱歉，未搜索到课程 "{}" ！'.format(keystr))
                    input("请继续...")
                    continue
                else:
                    print("编号\t课程名称\t\t\t开课单位\t\t网址链接")
                    cnt = 1
                    for course in courses:
                        print(align(str(cnt),5), align(course['name'],32), align(course['school'],18), course['url'])
                        cnt += 1
                    while True:
                        try:
                            order = int(input("输入一个要下载的课程编号(0退出): "))
                            if order >= 0 and order <= len(courses):
                                break
                        except ValueError:
                            pass
                        print("课程编号必须是一个0-{}的数字".format(len(courses)))
                    if order == 0:
                        continue
                    course_url = courses[order-1]['url']
            print("正在连接资源......")
            try:
                title = mooc.getSummary(course_url)
                mooc.getInfos()
                mooc.getContent(course_url)
            except (ConnectionResetError, HTTPError, AttributeError):
                input("该网址不存在！\n请继续...")
                continue
            except (timeout, URLError):
                input("请检查网络后继续...")
                continue
            except KeyError:
                print('很抱歉，无法获取 "{}" 对应的课程资源！'.format(course_url))
                input("请继续...")
                continue
            isShd = choice_hd()
            isdownload = mooc.download(isShd)
            while isdownload is False:
                redown = None
                while redown not in ('y','n'):
                    try: 
                        redown = input("是否继续[y/n]: ")
                    except KeyboardInterrupt: 
                        print()
                if redown == 'n':
                    break
                isdownload = mooc.download(isShd)
            if isdownload:
                print('"{}" 下载完毕!'.format(title[:title.rfind('__')]))
                print("下载路径: {}".format(mooc.rootDir))
                os.startfile(mooc.rootDir)
                input("请按回车键返回主界面...")
            elif isdownload is None:
                print('"{}" 还未开课！'.format(title[:title.rfind('__')]))
                input("请按回车键返回主界面...")
    except KeyboardInterrupt:
        print()
    finally:
        if (input("\n小哥哥，小姐姐，扫码领红包 …(⊙_⊙)… [y/n]: ") != 'n'):
            alipy = get_SourceFile(CODE)
            os.startfile(alipy)

def main():
    mooc = Mooc()
    try:
        UI_interface(mooc)
    except (KeyboardInterrupt, EOFError):
        pass
    os.system("pause")


if __name__ == '__main__':
    main()
