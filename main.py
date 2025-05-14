from modules.login_helper import init_session, asmr_login
from modules.playlist_api import fetch_playlists, fetch_playlist_works
from modules.downloader import batch_download, single_download
from modules.utils import load_config, ensure_dir
from modules.cli import cli_select_download
import os

def main():
    config = load_config('config.ini')
    ensure_dir(config.get('paths', 'download_path'))
    ensure_dir('data')
    session = init_session(config)
    if not asmr_login(session, config):
        print("登录失败")
        return
    try:
        cli_select_download(session, config)
    except KeyboardInterrupt:
        print("\n下载已取消，程序已安全退出。")

if __name__ == '__main__':
    main()