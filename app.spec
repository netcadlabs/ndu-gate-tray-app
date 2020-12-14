# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['ndu-gate-manager\\app.py'],
             pathex=['C:\\Users\\mythb\\Desktop\\CODE\\ndu-gate-tray-app'],
             binaries=[],
             datas=[
                ('ndu-gate-manager\\icons\\app_icon.ico', '.'),
                ('ndu-gate-manager\\config\\', 'config'),
                ('ndu-gate-manager\\icons\\', 'icons')
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
          [],
          exclude_binaries=True,
          name='NDUGateApp',
          debug=True,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          icon='ndu-gate-manager\\icons\\app_icon.ico',
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='NDUGateApp')
