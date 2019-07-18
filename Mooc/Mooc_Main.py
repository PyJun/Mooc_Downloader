'''
    Mooc下载器主程序

    作者：PyJun
    邮箱：py.jun@qq.com
'''

if __package__ is None:
    import sys
    sys.path.append('.\\')
    sys.path.append('..\\')
from Mooc.Mooc_Interface import *

def main():
    try:
        mooc_interface()
    except:
        pass

if __name__ == '__main__':
    main()
