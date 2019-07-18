'''
    Mooc 下载功能模块：调用 aria2c.exe 下载文件
'''

import os
import re
import subprocess
from time import sleep
from Mooc.Mooc_Config import *

__all__ = [
    "aria2_download_file", "DownloadFailed"
]

RE_SPEED = re.compile(r'\d+MiB/(\d+)MiB\((\d+)%\).*?DL:(\d*?\.?\d*?)([KM])iB')
RE_AVESPEED = re.compile(r'\|\s*?([\S]*?)([KM])iB/s\|')

class DownloadFailed(Exception):
    pass

def aria2_download_file(url, filename, dirname='.'):
    cnt = 0
    while cnt < 3:
        try:
            cmd = aira2_cmd.format(url=url, dirname=dirname, filename=filename)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True, encoding='utf8')
            lines = ''
            while p.poll() is None:
                line = p.stdout.readline().strip()
                if filename.endswith('.mp4') and line:
                    lines += line
                    match = RE_SPEED.search(line)
                    if match:
                        size, percent, speed, unit = match.groups()
                        percent = float(percent)
                        speed = float(speed)
                        if unit == 'K':
                            speed /= 1024
                        per = min(int(LENGTH*percent/100) , LENGTH)
                        print('\r  |-['+per*'*'+(LENGTH-per)*'.'+'] {:.0f}% {:.2f}M/s'.format(percent,speed),end=' (ctrl+c中断)')
            if p.returncode != 0:
                cnt += 1
                if cnt==1:
                    clear_files(dirname, filename)
                    sleep(0.16)
            else:
                if filename.endswith('.mp4'):
                    match = RE_AVESPEED.search(lines)
                    if match:
                        ave_speed, unit = match.groups()
                        ave_speed = float(ave_speed)
                        if unit == 'K':
                            ave_speed /= 1024
                    print('\r  |-['+LENGTH*'*'+'] {:.0f}% {:.2f}M/s'.format(100,ave_speed),end='  (完成)    \n')
                return
        finally:
            p.kill()   # 保证子进程已终止
    clear_files(dirname, filename)
    raise DownloadFailed("download failed")


def clear_files(dirname, filename):
    filepath = os.path.join(dirname, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    if os.path.exists(filepath+'.aria2'):
        os.remove(filepath+'.aria2')
