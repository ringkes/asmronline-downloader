# ASMR Online Downloader 模块化重构版

## 目录结构

```
asmronline/
├── config.ini
├── main.py                # 一键全流程入口
│
├── modules/
│   ├── login_helper.py
│   ├── playlist_api.py    # 播放列表相关API
│   ├── work_api.py        # 单个作品相关API
│   ├── downloader.py      # 下载核心
│   └── utils.py           # 工具函数
│
├── scripts/
│   ├── get_playlists.py   # 仅获取/刷新播放列表
│   ├── get_playlist.py    # 获取某个播放列表下所有work_id
│   └── asmr_downloader.py # 兼容旧入口
│
├── data/
│   ├── playlists.json
│   └── api_response.json
│
└── README.md
```

## 一键全流程用法

1. 配置 `config.ini`，设置账号、下载路径、index等参数。
2. 运行 `python main.py`，自动完成登录、获取列表、批量/单个下载。
3. 下载文件自动按 work_id 建独立文件夹。

## 主要模块说明
- `login_helper.py`：登录、会话初始化
- `playlist_api.py`：获取所有播放列表、获取指定播放列表下所有作品
- `work_api.py`：获取单个作品目录结构
- `downloader.py`：多线程下载、断点续传、限速
- `utils.py`：配置读取、路径处理、日志等

如需详细用法和参数说明，请参考各模块内注释。 

## 在根目录下创建 config.ini

```
[credentials]
username = 
password = 

[settings]
base_url = https://asmr.one
work_id = RJ01332053
download_speed = 5.0
max_workers = 4
max_retries = 3
timeout = 30
index = 0

[paths]
download_path = 
temp_path = temp

[proxy]
enable = false
type = http
host = 127.0.0.1
port = 7890
```