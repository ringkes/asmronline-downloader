import json
import requests
from modules.cli_output import print_works
from modules.utils import load_config

def fetch_playlists(session):
    """获取所有播放列表，返回列表[{index, name, works_count, id}, ...]"""
    API_URL_ALL = 'https://api.asmr-200.com/api/playlist/get-playlists?page=1&pageSize=96&filterBy=all'
    resp = session.get(API_URL_ALL)
    data = resp.json()
    playlists = data.get('playlists', [])
    if not playlists:
        playlists = data.get('data', {}).get('playlists', [])
    result = []
    for idx, item in enumerate(playlists, 1):
        result.append({
            'index': idx,
            'name': item.get('name', ''),
            'works_count': item.get('works_count', ''),
            'id': item.get('id', '')
        })
    # 可选：保存到data/playlists.json
    with open('data/playlists.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result

def fetch_playlist_works(session, playlist_id):
    """获取指定播放列表下所有作品work_id，返回work_id列表"""
    import math
    API_URL_TEMPLATE = 'https://api.asmr-200.com/api/playlist/get-playlist-works?id={id}&page=1&pageSize=12'
    all_works = []
    page = 1
    total_pages = 1
    while page <= total_pages:
        url = API_URL_TEMPLATE.format(id=playlist_id) + f'&page={page}'
        resp = session.get(url)
        data = resp.json()
        works = data.get('works', [])
        all_works.extend([f"RJ{str(w.get('id', ''))}" for w in works])
        if page == 1:
            pagination = data.get('pagination', {})
            total_count = pagination.get('totalCount', 0)
            page_size = pagination.get('pageSize', 12)
            total_pages = math.ceil(total_count / page_size)
        page += 1
    # 可选：保存到data/api_response.json
    with open('data/api_response.json', 'w', encoding='utf-8') as f:
        json.dump([{'work_id': wid} for wid in all_works], f, ensure_ascii=False, indent=2)
    return all_works

def fetch_and_save_recommend_for_user(session):
    """
    POST请求推荐API，分页获取所有数据，支持max_count，tags多语言，work_id格式，保存原始顺序，控制台美观输出。
    """
    url = "https://api.asmr-200.com/api/recommender/recommend-for-user"
    # 读取配置
    config = load_config('config.ini')
    page_size = int(config.get('settings', 'pageSize', fallback='20'))
    max_count = int(config.get('settings', 'max_count', fallback='0'))
    recommenderUuid = config.get('credentials', 'recommenderUuid', fallback=None)
    if not recommenderUuid:
        print('未提供 recommenderUuid，无法请求推荐接口')
        return
    payload = {
        "keyword": " ",
        "recommenderUuid": recommenderUuid,
        "page": 1,
        "pageSize": page_size,
        "subtitle": 0,
        "localSubtitledWorks": [],
        "withPlaylistStatus": []
    }
    headers = {
        "Content-Type": "application/json",
    }
    all_result = []
    page = 1
    total_count = None
    while True:
        payload["page"] = page
        resp = session.post(url, json=payload, headers=headers)
        print(f"请求第{page}页，状态码: {resp.status_code}")
        try:
            data = resp.json()
        except Exception as e:
            print('响应不是JSON:', resp.text)
            break
        works = data.get("works", [])
        for idx, w in enumerate(works, 1):
            aname = " ".join([v.get("name", "") for v in w.get("vas", [])])
            tags = " ".join([
                (
                    t.get("i18n", {}).get("zh-cn", {}).get("name")
                    or t.get("i18n", {}).get("ja-jp", {}).get("name")
                    or t.get("name", "")
                    or ""
                )
                for t in w.get("tags", [])
            ])
            item = {
                "index": len(all_result) + 1,
                "aname": aname,
                "name": w.get("name", ""),
                "release": w.get("release", ""),
                "title": w.get("title", ""),
                "tags": tags,
                "work_id": f"RJ{w.get('id', '')}"
            }
            all_result.append(item)
            if max_count > 0 and len(all_result) >= max_count:
                break
        # 分页判断
        if total_count is None:
            pagination = data.get("pagination", {})
            total_count = pagination.get("totalCount", 0)
        if len(all_result) >= total_count or not works or (max_count > 0 and len(all_result) >= max_count):
            break
        page += 1
    with open("data/recommend-for-user.json", "w", encoding="utf-8") as f:
        json.dump(all_result, f, ensure_ascii=False, indent=2)
    print(f'已保存所有作品主要字段到 recommend-for-user.json, 共{len(all_result)}条')
    print('\n每个作品的主要字段:')
    print_works(all_result)

def fetch_and_save_popular(session):
    """POST请求流行API并保存格式化结果到popular.json，字段与get_playlists.py一致"""
    url = "https://api.asmr-200.com/api/recommender/popular"
    payload = {
        "keyword": " ",
        "page": 1,
        "pageSize": 20,
        "subtitle": 0,
        "localSubtitledWorks": [],
        "withPlaylistStatus": []
    }
    resp = session.post(url, json=payload)
    try:
        data = resp.json()
    except Exception as e:
        print('响应不是JSON:', resp.text)
        return
    result = []
    for idx, w in enumerate(data.get("works", []), 1):
        aname = " ".join([v.get("name", "") for v in w.get("vas", [])])
        tags = " ".join([
            t.get("i18n", {}).get("zh-cn", {}).get("name", t.get("name", ""))
            for t in w.get("tags", []) if "zh-cn" in t.get("i18n", {})
        ])
        item = {
            "index": idx,
            "aname": aname,
            "name": w.get("name", ""),
            "release": w.get("release", ""),
            "title": w.get("title", ""),
            "tags": tags,
            "id": w.get("id", "")
        }
        result.append(item)
    with open("data/popular.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print('已保存所有作品主要字段到 popular.json')
    print('\n每个作品的主要字段:')
    for item in result:
        print(f"index: {item['index']} | title: {item['title']} | id: {item['id']} | aname: {item['aname']} | tags: {item['tags']} | release: {item['release']}") 