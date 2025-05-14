import requests

def init_session(config):
    """
    初始化 requests.Session，设置 headers 和代理。
    """
    session = requests.Session()
    # 设置基本请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate',  # 去掉 br
        'Connection': 'keep-alive',
    }
    session.headers.update(headers)
    # 设置代理
    if config.getboolean('proxy', 'enable'):
        proxy_type = config.get('proxy', 'type')
        proxy_host = config.get('proxy', 'host')
        proxy_port = config.get('proxy', 'port')
        proxies = {
            'http': f'{proxy_type}://{proxy_host}:{proxy_port}',
            'https': f'{proxy_type}://{proxy_host}:{proxy_port}'
        }
        session.proxies.update(proxies)
    return session

def asmr_login(session, config):
    """
    登录ASMR.ONE账号，获取token，成功返回True，失败返回False。
    """
    try:
        username = config.get('credentials', 'username')
        password = config.get('credentials', 'password')
        if not username or not password:
            print("错误：请在config.ini中设置用户名和密码")
            return False

        # 登录接口
        url = 'https://api.asmr.one/api/auth/me'
        data = {
            'name': username,
            'password': password
        }

        # 代理
        proxies = None
        if config.getboolean('proxy', 'enable'):
            proxy_type = config.get('proxy', 'type')
            proxy_host = config.get('proxy', 'host')
            proxy_port = config.get('proxy', 'port')
            proxies = {
                'http': f'{proxy_type}://{proxy_host}:{proxy_port}',
                'https': f'{proxy_type}://{proxy_host}:{proxy_port}'
            }

        # 发起登录请求（表单方式）
        response = session.post(url, data=data, proxies=proxies)
        print("响应Content-Type:", response.headers.get("Content-Type"))
        print("响应前200字符:", response.content[:200])

        try:
            req = response.json()
        except Exception as e:
            print(f"登录响应不是JSON: {response.text}")
            return False

        if req.get('user', {}).get('loggedIn'):
            token = req.get('token')
            session.headers.update({'Authorization': f'Bearer {token}'})
            print("登录成功！")
            return True
        else:
            print(f"登录失败：{req.get('error', '未知错误')}")
            return False
    except Exception as e:
        print(f"登录过程中出错：{str(e)}")
        return False 