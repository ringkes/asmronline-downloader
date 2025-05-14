def fetch_work_structure(session, work_id):
    """获取单个作品的目录结构，返回结构体（list）"""
    # 去除RJ前缀和前导0
    if isinstance(work_id, str) and work_id.upper().startswith('RJ'):
        work_id = work_id[2:]
    work_id = work_id.lstrip('0')
    url = f"https://api.asmr.one/api/tracks/{work_id}?v=1"
    resp = session.get(url)
    try:
        req = resp.json()
        if isinstance(req, list):
            return req
        else:
            print("API返回内容不是列表，内容：", req)
            return None
    except Exception as e:
        print("目录API响应不是JSON:", resp.text)
        return None 