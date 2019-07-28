'''
    www.icourses.cn/mooc/ 下的资源共享课下载解析
'''

import os
import re
import json
if __package__ is None:
    import sys
    sys.path.append('..\\')
    sys.path.append('..\\..\\')
from Mooc.Mooc_Config import *
from Mooc.Mooc_Download import *
from Mooc.Mooc_Request import *
from Mooc.Icourses.Icourse_Config import *
from Mooc.Icourses.Icourse_Base import *

__all__ = [
    "Icourse_Mooc"
]

class Icourse_Mooc(Icourse_Base):
    url_title = 'http://www.icourses.cn/sCourse/course_{}.html'
    url_id = 'http://www.icourses.cn/web/sword/portal/shareChapter?cid='
    url_course = 'http://www.icourses.cn/web//sword/portal/getRess' 
    url_assign = 'http://www.icourses.cn/web/sword/portal/assignments?cid='
    url_paper = 'http://www.icourses.cn/web/sword/portal/testPaper?cid='
    url_source = 'http://www.icourses.cn/web/sword/portal/sharerSource?cid='

    def __init__(self, mode=IS_MP4|IS_PDF|IS_PAPER|IS_SOURCE):
        super().__init__()
        self.mode = mode

    def _get_cid(self, url):
        self.cid = None
        match = courses_re.get('icourse_mooc').match(url)
        if match:
            cid = match.group(3) or match.group(5)
            self.cid = cid 

    def _get_title(self):
        if not self.cid:
            return
        self.title = None
        url = self.url_title.format(self.cid)
        text = request_get(url)
        match_name = re.search(r'<div +class="course-title clearfix">\s*<p +class="pull-left">(.*?)</p>', text)
        match_school = re.search(r'<span +class="pull-left">学校:</span>\s*<p +class="course-information-hour pull-left">(.*?)</p>', text)
        if match_name and match_school:
            title_name = match_name.group(1) + '__' + match_school.group(1)
            self.title = winre.sub('', title_name)[:WIN_LENGTH]

    def _get_infos(self):
        if not self.cid:
            return
        self.infos = []
        url1 = self.url_id + self.cid
        url2 = self.url_assign + self.cid
        text1 = request_get(url1)
        text2 = request_get(url2)
        chapter_ids = re.findall(r'<li +data-id="(\d+)" +class="chapter-bind-click panel[\s\S]*?">', text1)
        chapter_names = re.findall(r'<a +class="chapter-title-text"[\s\S]*?>([\s\S]*?)</a>', text1)
        chapter_ptext = re.findall(r'<div[\s\S]*?id="collapse(\d+)"[\s\S]*?<div([\s\S]*?)</div>', text2)
        match_str = r'<div[\s\S]*?id="collapse{}-{}"([\s\S]*?)</div>'
        re_pdf = re.compile(r'data-class="media"[\s\S]*?data-title="([\s\S]*?)"[\s\S]*?data-url="(.*?)"')
        for _id, name in zip(chapter_ids, chapter_names):
            self.infos.append({'id': _id, 'name': winre.sub('',name)[:WIN_LENGTH], 'units':[], 'pdfs':[]})
        for index, ptext in chapter_ptext:
            inx = int(index)-1
            pdfs = re_pdf.findall(ptext)
            pdf_list = [{'name':winre.sub('', pdf[0])[:WIN_LENGTH], 'url':pdf[1]} for pdf in pdfs]
            self.infos[inx]['pdfs'] = pdf_list
        unit_list = re.findall(r'<a +class="chapter-body-content-text section-event-t no-load"[\s\S]*?data-secId="(\d+)"[\s\S]*?<span +class="chapter-s">(\d+)</span><span>.</span>\s*?<span +class="chapter-t">(\d+)</span>(.*?)</a>', text1)
        for unit_id,unit_inx1, unit_inx2,unit_name in unit_list:
            inx1 = int(unit_inx1)-1
            inx2 = int(unit_inx2)-1
            self.infos[inx1]['units'].append({'id': unit_id, 'name': winre.sub('',unit_name)[:WIN_LENGTH], 'pdfs':[]})
            m_str = match_str.format(unit_inx1, unit_inx2)
            match_ptext = re.search(m_str, text2)
            if match_ptext:
                ptext = match_ptext.group(1)
                pdfs = re_pdf.findall(ptext)
                pdf_list = [{'name':winre.sub('', pdf[0])[:WIN_LENGTH], 'url':pdf[1]} for pdf in pdfs]
                self.infos[inx1]['units'][inx2]['pdfs'] = pdf_list

    def _get_course_links(self, sid):
        mp4_list = []
        pdf_list = []
        data = {'sectionId': sid}
        text = request_post(self.url_course, data)
        #!!! except json.decoder.JSONDecodeError        
        infos = json.loads(text)
        if infos['model']['listRes'] :
            reslist = infos['model']['listRes']
            for res in reslist:
                if res['mediaType'] == 'mp4':
                    if 'fullResUrl' in res:
                        mp4_list.append((res['fullResUrl'], res['title']))
                elif res['mediaType'] in ('ppt', 'pdf'):
                    if 'fullResUrl' in res:
                        pdf_list.append((res['fullResUrl'], res['title']))
        return mp4_list, pdf_list

    def _get_paper_links(self):
        url = self.url_paper + self.cid
        paper_list = []
        text = request_get(url)
        match_text = re.findall(r'<a +data-class="media"((.|\n)+?)>', text)
        re_url = re.compile(r'data-url="(.*?)"')
        re_title = re.compile(r'data-title="(.*?)"')
        for m_text in match_text:
            link_list = re_url.findall(m_text[0])
            title_list = re_title.findall(m_text[0])
            paper_list += list(zip(link_list, title_list))
        return paper_list

    def _get_source_links(self):
        url = self.url_source + self.cid
        source_list = []
        text = request_get(url)
        match_text = re.findall(r'<a +class="courseshareresources-content clearfix"((.|\n)+?)>', text)
        re_url = re.compile(r'data-url="(.*?)"')
        re_title = re.compile(r'data-title="(.*?)"')
        for m_text in match_text:
            link_list = re_url.findall(m_text[0])
            title_list = re_title.findall(m_text[0])
            source_list += list(zip(link_list, title_list))
        return source_list

    def _download(self):
        print('\n{:^{}s}'.format(self.title, LEN_S))
        self.rootDir = rootDir = os.path.join(PATH, self.title)
        if not os.path.exists(rootDir):
            os.mkdir(rootDir)
        Icourse_Base.potplayer.init(rootDir)
        if (self.mode & IS_MP4) or (self.mode & IS_PDF):
            courseDir = os.path.join(rootDir, COURSENAME)
            if not os.path.exists(courseDir):
                os.mkdir(courseDir)
            print('-'*LEN_+'下载课程'+'-'*LEN_)
            Icourse_Base.potplayer.enable()
            for cnt1, info in enumerate(self.infos, 1):
                chapter = '{'+str(cnt1)+'}--'+info['name']
                print(chapter)
                chapterDir = os.path.join(courseDir, chapter)
                if not os.path.exists(chapterDir):
                    os.mkdir(chapterDir)
                mp4_list, pdf_list = self._get_course_links(info['id'])
                pdf_list += [(pdf['url'], pdf['name']) for pdf in info['pdfs']]
                if self.mode & IS_PDF:
                    self.download_pdf_list(chapterDir, pdf_list, '{}.'.format(cnt1))
                if self.mode & IS_MP4:
                    self.download_video_list(chapterDir, mp4_list, '{}.'.format(cnt1))
                for cnt2, unit in enumerate(info['units'],1):
                    lesson = '{'+str(cnt2)+'}--'+unit['name']
                    print("  "+lesson)
                    lessonDir = os.path.join(chapterDir, lesson)
                    if not os.path.exists(lessonDir):
                        os.mkdir(lessonDir)
                    mp4_list, pdf_list = self._get_course_links(unit['id'])
                    pdf_list += [(pdf['url'], pdf['name']) for pdf in unit['pdfs']]
                    if self.mode & IS_PDF:
                        self.download_pdf_list(lessonDir, pdf_list, '{}.{}.'.format(cnt1,cnt2))
                    if self.mode & IS_MP4:
                        self.download_video_list(lessonDir, mp4_list, '{}.{}.'.format(cnt1,cnt2))
        if self.mode & IS_PAPER:
            paperDir = os.path.join(rootDir, PAPERNAME)
            if not os.path.exists(paperDir):
                os.mkdir(paperDir)
            print("-"*LEN_+"下载试卷"+"-"*LEN_)
            paper_list = self._get_paper_links()
            self.download_pdf_list(paperDir, paper_list)
        if self.mode & IS_SOURCE:
            sourceDir = os.path.join(rootDir, SOURCENAME)
            if not os.path.exists(sourceDir):
                os.mkdir(sourceDir)
            print("-"*LEN_+"下载资源"+"-"*LEN_)
            Icourse_Base.potplayer.disable()
            source_list = self._get_source_links()
            pdf_list = list(filter(lambda x:x[0].endswith('.pdf'), source_list))
            mp4_list = list(filter(lambda x:x[0].endswith('.mp4'), source_list))
            self.download_pdf_list(sourceDir, pdf_list)
            self.download_video_list(sourceDir, mp4_list)

    def set_mode(self):
        while True:
            try:
                instr = input(
                    "    视频:[1]    +    课件:[2]    +    试卷:[4]    +    资源:[8]\n"
                    "请输入一个0-15的数选择性下载内容(如15表示全部下载,15=1+2+4+8) [0退出]: "
                    )
                if not instr:
                    continue
                try:
                    innum = int(instr)
                    if innum == 0:
                        return False
                    elif  1 <= innum <= 15:
                        self.mode = innum
                        return True
                    else:
                        print("请输入一个0-15之间的整数!")
                        continue
                except ValueError:
                    print("请输入一个0-15之间的整数!")
            except KeyboardInterrupt:
                print()


def main():
    # url = 'http://www.icourses.cn/sCourse/course_4860.html'
    url = 'http://www.icourses.cn/web/sword/portal/shareDetails?cId=4860#/course/chapter'
    # url = 'https://www.icourses.cn/sCourse/course_6661.html'
    # url = 'http://www.icourses.cn/sCourse/course_3459.html'
    icourse_mooc = Icourse_Mooc()
    if (icourse_mooc.set_mode()):
        icourse_mooc.prepare(url)
        icourse_mooc.download()


if __name__ == '__main__':
    main()
