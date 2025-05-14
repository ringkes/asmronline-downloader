import requests
import configparser

def init_session(config: configparser.ConfigParser):
    session = requests.Session()
    # 可根据需要设置headers、代理等
    return session

def asmr_login(session, config):
    """登录ASMR.ONE账号，获取token"""
    username = config.get('credentials', 'username')
    password = config.get('credentials', 'password')
    url = 'https://api.asmr.one/api/auth/me'
    data = {'name': username, 'password': password}
    resp = session.post(url, data=data)
    try:
        req = resp.json()
        if req.get('user', {}).get('loggedIn'):
            token = req.get('token')
            session.headers.update({'authorization': f'Bearer {token}'})
            return True
        else:
            print('登录失败:', req)
            return False
    except Exception as e:
        print('登录响应异常:', resp.text)
        return False 