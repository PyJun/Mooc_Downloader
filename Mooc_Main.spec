# -*- mode: python -*-

block_cipher = None


a = Analysis(['Mooc\\Mooc_Main.py',
              'Mooc\\Mooc_Base.py',
              'Mooc\\Mooc_Config.py',
              'Mooc\\Mooc_Download.py',
              'Mooc\\Mooc_Interface.py',
              'Mooc\\Mooc_Potplayer.py',
              'Mooc\\Mooc_Request.py',

              'Mooc\\Icourses\\Icourse_Base.py',
              'Mooc\\Icourses\\Icourse_Config.py',
              'Mooc\\Icourses\\Icourse_Cuoc.py',
              'Mooc\\Icourses\\Icourse_Mooc.py',

              'Mooc\\Icourse163\\Icourse163_Base.py',
              'Mooc\\Icourse163\\Icourse163_Config.py',
              'Mooc\\Icourse163\\Icourse163_Mooc.py'
              ],
             pathex=['D:\\Masterpiece\\Mooc\\new-package'],
             binaries=[],
             datas=[
              ('Mooc\\aria2c.exe', '.'),
              ('Mooc\\Alipay.jpg', '.')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='Mooc_Main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='Mooc\\Mooc.ico')
