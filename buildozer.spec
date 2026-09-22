[app]
title = XSMB Android
package.name = xsmb
package.domain = com.thanhhajbgg
version = 1.1.0
android.numeric_version = 110
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt,html,css,js,csv
source.include_patterns = assets/*,src/*,web/*
source.exclude_dirs = tests,bin,.buildozer,__pycache__,.github,.git,docs,android_src,android_config,p4a-recipes,scripts,.venv
source.exclude_patterns = *.pyc,*.pyo,*.md,*.bat,*.ps1,*.db,*.sqlite,*.log

# Python/numpy match the pinned p4a recipes. Do not force an old NumPy
# version into the modern Meson-based recipe.
requirements = python3==3.12.10,hostpython3==3.12.10,kivy==2.3.1,numpy,beautifulsoup4==4.13.4,openpyxl==3.1.5,chardet==5.2.0,requests==2.32.4,urllib3==2.5.0,certifi==2025.4.26,idna==3.10,pyjnius,android,sqlite3,openssl,reportlab
p4a.bootstrap = sdl2
p4a.fork = kivy
p4a.branch = master
p4a.commit = 58d21141f17c889bf8585f5665921d72028f8831
p4a.local_recipes = ./p4a-recipes

orientation = portrait
fullscreen = 0
# No missing custom icon/presplash: use Buildozer's bundled defaults.
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 35
android.minapi = 24
android.ndk = 28c
android.ndk_api = 24
android.archs = arm64-v8a
android.allow_backup = False
android.accept_sdk_license = True
android.enable_androidx = True
android.add_src = android_src
android.extra_manifest_application_arguments = android_config/application.xml
android.logcat_filters = *:S python:D

[buildozer]
log_level = 2
warn_on_root = 0
