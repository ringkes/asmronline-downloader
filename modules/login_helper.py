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
            # 登录成功后自动写入recommenderUuid和token到config.ini
            user = req.get('user', {})
            recommenderUuid = user.get('recommenderUuid', '')
            if recommenderUuid or token:
                if not config.has_section('credentials'):
                    config.add_section('credentials')
                config.set('credentials', 'recommenderUuid', recommenderUuid)
                config.set('credentials', 'token', token)
                with open('config.ini', 'w', encoding='utf-8') as f:
                    config.write(f)
                # print('recommenderUuid 和 token 已写入 config.ini')
            # 登录成功后自动获取并写入recommenderUuid（保留原有功能）
            fetch_and_save_recommender_uuid(session)
            return True
        else:
            print('登录失败:', req)
            return False
    except Exception as e:
        print('登录响应异常:', resp.text)
        return False

def update_config_recommender_uuid(uuid):
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    if not config.has_section('credentials'):
        config.add_section('credentials')
    config.set('credentials', 'recommenderUuid', uuid)
    with open('config.ini', 'w', encoding='utf-8') as f:
        config.write(f)

def fetch_and_save_recommender_uuid(session):
    url = "https://api.asmr-200.com/api/auth/me"
    resp = session.get(url)
    try:
        data = resp.json()
        uuid = data.get("user", {}).get("recommenderUuid")
        if uuid:
            update_config_recommender_uuid(uuid)
            print(f"已自动写入 recommenderUuid: {uuid} 到 config.ini")
        else:
            print("未获取到 recommenderUuid")
    except Exception as e:
        print("获取 recommenderUuid 失败:", e)
