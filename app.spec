# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['service_manager\\app.py'],
             pathex=['C:\\Users\\Netcad\\Desktop\\CODE\\ndu-gate-tray-app'],
             binaries=[],
             datas=[
                ('service_manager\\icons\\app_icon.ico', '.'),
                ('service_manager\\config\\', 'config'),
                ('service_manager\\icons\\', 'icons')
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
          icon='service_manager\\icons\\app_icon.ico',
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='NDUGateApp')
