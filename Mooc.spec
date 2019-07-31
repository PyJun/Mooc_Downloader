# -*- mode: python -*-

block_cipher = None


a = Analysis(['Mooc\\Mooc_Main.py'],
             pathex=['.'],
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
          name='Mooc-3.4.2',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='Mooc\\Mooc.ico')
