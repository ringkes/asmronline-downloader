import configparser
from modules.playlist_api import fetch_playlists, fetch_playlist_works, fetch_and_save_recommend_for_user, fetch_and_save_popular
from modules.downloader import batch_download, single_download
from modules.utils import load_config

def update_config_index(index):
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    config.set('settings', 'index', str(index))
    with open('config.ini', 'w', encoding='utf-8') as f:
        config.write(f)

def update_config_work_id(work_id):
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    config.set('settings', 'work_id', work_id)
    with open('config.ini', 'w', encoding='utf-8') as f:
        config.write(f)

def cli_select_download(session, config):
    # 刷新播放列表
    playlists = fetch_playlists(session)
    print("\n已刷新 data/playlists.json，当前播放列表如下：")
    for item in playlists:
        print(f"index: {item['index']} | name: {item['name']} | works_count: {item['works_count']}")
    print("\n请输入要下载的 index（0 表示单个下载，输入对应数字批量下载播放列表，popular 或 recommend 可直接获取推荐/流行列表）：")
    while True:
        user_index = input("index = ").strip()
        if user_index.lower() in ["popular", "recommend"]:
            break
        try:
            user_index_int = int(user_index)
            if user_index_int == 0 or (1 <= user_index_int <= len(playlists)):
                user_index = user_index_int
                break
            else:
                print(f"请输入 0 或 1~{len(playlists)} 之间的数字，或 popular/recommend！")
        except Exception:
            print("请输入有效数字或 popular/recommend！")
    # 更新config.ini
    if isinstance(user_index, int):
        update_config_index(user_index)
        config = load_config('config.ini')
        if user_index == 0:
            default_work_id = config.get('settings', 'work_id')
            user_work_id = input(f"请输入要下载的 work_id（回车使用默认值 {default_work_id}）：").strip()
            if not user_work_id:
                user_work_id = default_work_id
            update_config_work_id(user_work_id)
            config = load_config('config.ini')
            print(f"\n即将下载单个作品：{user_work_id}")
            single_download(session, user_work_id, config)
        else:
            playlist_id = playlists[user_index-1]['id']
            print(f"\n即将下载第{user_index}个播放列表：{playlists[user_index-1]['name']}")
            work_ids = fetch_playlist_works(session, playlist_id)
            batch_download(session, work_ids, config)
    elif isinstance(user_index, str) and user_index.lower() == "popular":
        print("\n即将获取流行作品列表并保存到 popular.json ...")
        fetch_and_save_popular(session)
        print("已保存 popular.json")
    elif isinstance(user_index, str) and user_index.lower() == "recommend":
        print("\n即将获取推荐作品列表并保存到 recommend-for-user.json ...")
        fetch_and_save_recommend_for_user(session)
        print("已保存 recommend-for-user.json")
