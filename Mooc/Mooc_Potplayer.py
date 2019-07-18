'''
    Mooc 生成 potplayer 播放列表 dpl 文件的类
'''

import os
from functools import wraps
from Mooc.Mooc_Config import * 

__all__ = [
    "Mooc_Potplayer"
]

class Mooc_Potplayer():
    def __init__(self):
        self.cnt = 0
        self.lines = []
        self.available = False

    def init(self, rootdir):
        self.rootdir = rootdir
        self.listpath = os.path.join(rootdir, PLAYLIST)
        self.listpath_back = os.path.join(rootdir, PALYBACK)
        self.batpath = os.path.join(rootdir, BATNAME)

    def __call__(self, func):
        @wraps(func)
        def wrap_func(*args, **kwargs):
            succeed = func(*args, **kwargs)
            if self.available and succeed:
                self.cnt += 1
                video_dir = kwargs['video_dir']
                video_name = kwargs['video_name']
                video_path = os.path.join(video_dir, video_name+'.mp4')
                video_relpath = os.path.relpath(video_path, self.rootdir)
                if self.lines == [] and self.cnt == 1:
                    self.lines.append('DAUMPLAYLIST\n')
                    self.lines.append("playname=%s\n"%(video_relpath))
                    with open(self.batpath, 'w') as batfile:
                        batfile.write(BATSTRING)
                self.lines.append("%d*file*%s\n"%(self.cnt,video_relpath))
                self.lines.append("%d*title*%s\n"%(self.cnt,video_name))
                self.update()
            return succeed
        return wrap_func

    def update(self):
        with open(self.listpath, 'w', encoding='utf8') as listfile:
            listfile.writelines(self.lines)
        with open(self.listpath_back, 'w',  encoding='utf8') as listfile:
            listfile.writelines(self.lines)

    def enable(self):
        self.cnt = 0
        self.lines = []
        self.available = True

    def disable(self):
        self.available = False
