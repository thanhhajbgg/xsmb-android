[app]
title = XSMB Android
package.name = xsmb
package.domain = com.thanhhajbgg
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt,html,css,js,xlsx,csv
source.include_patterns = assets/*,src/*,web/*
source.exclude_dirs = tests,bin,.buildozer,__pycache__,.github,docs
source.exclude_patterns = *.pyc,*.pyo,*.md,*.bat,*.ps1

version = 1.0.0

# Hạ numpy xuống 1.22.4 để tương thích tốt hơn với Android
requirements = python3,kivy==2.3.0,cython,numpy==1.22.4,beautifulsoup4,openpyxl,chardet,requests,urllib3,certifi,idna,pyjnius,android

# Giữ nhánh develop để có các bản vá lỗi mới nhất
p4a.bootstrap = sdl2
p4a.fork = kivy
p4a.branch = develop

orientation = portrait
fullscreen = 0
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACCESS_WIFI_STATE,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.debug_manifest_xml = False
android.release_manifest_xml = False

android.logcat_filters = *:S python:D
android.copy_libs = 1
android.enable_androidx = True
android.enable_google_analytics_automated = False

[buildozer]
log_level = 2
warn_on_root = 1
