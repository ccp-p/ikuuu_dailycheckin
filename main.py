import requests, json, re, os

from playwright.sync_api import sync_playwright
import requests, json, re, os, time

email = os.environ.get('EMAIL')
passwd = os.environ.get('PASSWD')
SCKEY = os.environ.get('SCKEY')

host = 'https://ikuuu.org'
login_url = f'{host}/auth/login'
check_url = f'{host}/user/checkin'

try:
    print('启动无头浏览器进行登录...')
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(login_url)
        
        # 输入账号密码
        page.fill('input#email', email)
        page.fill('input#password', passwd)
        
        print('等待验证码加载并点击...')
        # 等待并点击图形验证区域
        page.wait_for_selector('.geetest_btn_click', timeout=10000)
        page.click('.geetest_btn_click')
        
        # 留点时间给极验完成验证，有时候可能需要滑块，简单点击通过的场景：
        time.sleep(3)
        
        print('点击登录按钮...')
        page.click('button.login')
        time.sleep(3)
        
        # 获取登录后的cookies传递给requests
        cookies = page.context.cookies()
        session_cookies = {c['name']: c['value'] for c in cookies}
        browser.close()
        
    print('登录成功，准备签到...')
    
    session = requests.session()
    session.cookies.update(session_cookies)
    header = {
        'origin': host,
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    
    # 进行签到
    result = json.loads(session.post(url=check_url,headers=header).text)
    print(result['msg'])
    content = result['msg']
    
    # 进行推送
    if SCKEY != '':
       push_url = 'https://sctapi.ftqq.com/{}.send?title=ikuu签到-{}'.format(SCKEY, content)
       requests.post(url=push_url)
       print('推送成功')
except Exception as e:
    content = f'签到失败: {str(e)}'
    print(content)
    if SCKEY != '':
        push_url = 'https://sctapi.ftqq.com/{}.send?title=ikuu签到-{}'.format(SCKEY, content)
        requests.post(url=push_url)
