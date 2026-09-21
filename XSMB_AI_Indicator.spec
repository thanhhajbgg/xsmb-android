# Build on Windows. Includes local dashboard and Vietnamese PDF font.
a = Analysis(['run_desktop.py'], pathex=[], binaries=[],
    datas=[('web','web'),('assets','assets')], hiddenimports=[], hookspath=[],
    hooksconfig={}, runtime_hooks=[], excludes=['flask','pytest'], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz,a.scripts,a.binaries,a.datas,[],name='XSMB_AI_Indicator_V2_2_PRO',
    debug=False,bootloader_ignore_signals=False,strip=False,upx=False,console=False)
