[app]
title = XSMB Intelligence Studio
package.name = xsmbstudio
package.domain = vn.xsmb

source.dir = .
source.include_exts = py,png,jpg,jpeg,atlas,json,csv,html,css,js,md,txt,ttf,otf
source.exclude_dirs = .venv,tests,dist,build,__pycache__,.git,docs,.buildozer,bin,.github
source.exclude_patterns = *.spec,*.bat,*.ps1,requirements-dev.txt,*.apk,*.exe,build.log

version = 2.2.0

# BỎ reportlab, bỏ lxml, bỏ pymupdf — chỉ giữ những gì chắc chắn build được
requirements = python3,kivy==2.3.0,numpy==1.26.4,beautifulsoup4,openpyxl,chardet,requests,urllib3,certifi,idna

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,ACCESS_NETWORK_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
