from login_helper import init_session, asmr_login
import configparser
import json
import requests
from modules.cli_output import print_works

# 用户创建的播放列表url
API_URL_ALL = 'https://api.asmr-200.com/api/recommender/recommend-for-user'


def sort_result(result):
    """
    对作品列表排序：
    先按 release 时间倒序（最新在前），再按 name 升序，最后按 aname 升序。
    :param result: 作品字典列表
    :return: 排序后的新列表
    """
    return sorted(result, key=lambda x: (
        -int(x["release"].replace('-', '') or 0),
        x["name"],
        x["aname"]
    ))


def save_to_json(data, filename):
    """将数据保存到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    # 加载配置
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    # 初始化 session
    session = init_session(config)
    # 登录
    if not asmr_login(session, config):
        print('登录失败，无法获取播放列表')
        return
    # 从配置读取 pageSize 和 max_count
    page_size = int(config.get('settings', 'pageSize', fallback='20'))
    max_count = int(config.get('settings', 'max_count', fallback='0'))  # 0表示不限制
    url = "https://api.asmr-200.com/api/recommender/recommend-for-user"
    payload = {
        "keyword": " ",
        "recommenderUuid": "4d8647d8-3959-43d7-adef-f042f16bf3a2",
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
        resp = requests.post(url, json=payload, headers=headers)
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
                "id": w.get("id", "")
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
    # 排序并格式化 work_id
    for item in all_result:
        item["work_id"] = f"RJ{item['id']}"
    for item in all_result:
        del item["id"]
    save_to_json(all_result, "recommend-for-user.json")
    print(f'已保存所有作品主要字段到 recommend-for-user.json, 共{len(all_result)}条')
    print('\n每个作品的主要字段:')
    print_works(all_result)


if __name__ == '__main__':
    main()
