import json

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