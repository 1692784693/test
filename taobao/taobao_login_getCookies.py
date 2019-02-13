import asyncio
import random
import time
from pyppeteer import launch
from retrying import retry


async def taoBaoLogin(username='18269411189', password='pang15878042803', url='https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.taobao.com%2F'):
    #'headless': False如果想要浏览器隐藏更改False为True
    # 127.0.0.1:1080为代理ip和端口，这个根据自己的本地代理进行更改，如果是vps里或者全局模式可以删除掉'--proxy-server=127.0.0.1:1080'
    browser = await launch({'headless': False, 'args': ['--no-sandbox',"–ash-host-window-bounds=1024x768"], })
    page = await browser.newPage()
    # await page.setViewport({width: 1920, height: 1080})
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
    await page.goto(url)
    await page.evaluate(
        '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')  # 以下为插入中间js，将淘宝会为了检测浏览器而调用的js修改其结果。
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')

    await page.click('#J_QRCodeLogin > div.login-links > a.forget-pwd.J_Quick2Static')
    page.mouse
    time.sleep(1)
    # 输入用户名，密码
    await page.type('#TPL_username_1', username, {'delay': input_time_random() - 50})   #delay是限制输入的时间
    await page.type('#TPL_password_1', password, {'delay': input_time_random()})
    time.sleep(2)
    # 检测页面是否有滑块。原理是检测页面元素。
    slider = await page.Jeval('#nocaptcha', 'node => node.style')  # 是否有滑块

    if slider:
        print('当前页面出现滑块')
        # await page.screenshot({'path': './headless-login-slide.png'}) # 截图测试
        flag, page = await mouse_slide(page=page)  # js拉动滑块过去。
        if flag:
            await page.keyboard.press('Enter')  # 确保内容输入完毕，少数页面会自动完成按钮点击
            print("print enter", flag)
            await page.evaluate('''document.getElementById("J_SubmitStatic").click()''')  # 如果无法通过回车键完成点击，就调用js模拟点击登录按钮。
            time.sleep(2)
            # cookies_list = await page.cookies()
            # print(cookies_list)
            return await get_cookie(page)  # 导出cookie 完成登陆后就可以拿着cookie玩各种各样的事情了。
    else:
        print("")
        await page.keyboard.press('Enter')
        print("print enter")
        await page.evaluate('''document.getElementById("J_SubmitStatic").click()''')
        await page.waitFor(20)
        await page.waitForNavigation()

        try:
            global error  # 检测是否是账号密码错误
            print("error_1:", error)
            error = await page.Jeval('.error', 'node => node.textContent')
            print("error_2:", error)
        except Exception as e:
            error = None
        finally:
            if error:
                print('确保账户安全重新入输入')
                # 程序退出。
                loop.close()
            else:
                print(page.url)
                return await get_cookie(page)



# 获取登录后cookie
async def get_cookie(page):
    # res = await page.content()
    cookies_list = await page.cookies()
    cookies = ''
    for cookie in cookies_list:
        str_cookie = '{0}={1};'
        str_cookie = str_cookie.format(cookie.get('name'), cookie.get('value'))
        cookies += str_cookie
    # print(cookies)
    return cookies

def retry_if_result_none(result):
    return result is None

@retry(retry_on_result=retry_if_result_none)
async def mouse_slide(page=None):
    await asyncio.sleep(2)
    try:
        # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
        await page.hover('#nc_1_n1z')  # 不同场景的验证码模块能名字不同。
        await page.mouse.down()
        await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
        await page.mouse.up()
    except Exception as e:
        print(e, ':验证失败')
        return None, page
    else:
        await asyncio.sleep(2)
        # 判断是否通过
        slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
        if slider_again != '验证通过':
            return None, page
        else:
            # await page.screenshot({'path': './headless-slide-result.png'}) # 截图测试
            print('验证通过')
            return 1, page


def input_time_random():
    return random.randint(100, 151)

if __name__ == '__main__':
    # username = '18269411189'
    # password = r'pang15878042803'
    # url = 'https://login.taobao.com/member/login.jhtml?redirectURL=https%3A%2F%2Fwww.taobao.com%2F'
    loop = asyncio.get_event_loop()
    task = asyncio.ensure_future(taoBaoLogin())
    loop.run_until_complete(task)
    cookie = task.result()
    print(cookie)   #unb=2703869308;_uab_collina=154866322762582270247938;log=lty=Ug%3D%3D;cookieCheck=7872;_tb_token_=e1317e3f3b66e;t=73bc225db73c962e43c4520391b0d73e;cna=uqfVFEHfzXYCAXFhfYsXC/B0;cookie2=165b688151cc409cc26dda175af4cd2a;lid=%E4%B8%B6%E5%A2%A8%E8%BF%B9%E5%A2%A8%E8%BF%B9%E4%B8%B6;v=0;sg=%E4%B8%B688;_l_g_=Ug%3D%3D;skt=e6c75d7eb4fcd7ef;l=bBLm9kBrvsmSww31BOCZ-Fzi7M_OSIRYSuJaIsEDi_5KQ6T_lf_OlW8uaF96VjfR_DLBq2Fvhwy9-etuw;lc=VypQ05%2Fd7mboplkQi7OisSs%3D;cookie1=Vv8QuiguQsJfpsaa27SYQYEt7MibMYhFmijePk24YbM%3D;csg=348f9a94;uc3=vt3=F8dByE7ampH5%2Beu%2Ft9w%3D&id2=UU8IP0hJQI9%2Fow%3D%3D&nk2=u%2F4KzUxHYhFpELE8&lg2=UtASsssmOIJ0bQ%3D%3D;existShop=MTU0ODY2MzI0MA%3D%3D;tracknick=%5Cu4E36%5Cu58A8%5Cu8FF9%5Cu58A8%5Cu8FF9%5Cu4E36;lgc=%5Cu4E36%5Cu58A8%5Cu8FF9%5Cu58A8%5Cu8FF9%5Cu4E36;_cc_=W5iHLLyFfA%3D%3D;mt=ci=5_1;dnk=%5Cu4E36%5Cu58A8%5Cu8FF9%5Cu58A8%5Cu8FF9%5Cu4E36;_nk_=%5Cu4E36%5Cu58A8%5Cu8FF9%5Cu58A8%5Cu8FF9%5Cu4E36;cookie17=UU8IP0hJQI9%2Fow%3D%3D;tg=0;thw=cn;uc1=cookie16=U%2BGCWk%2F74Mx5tgzv3dWpnhjPaQ%3D%3D&cookie21=WqG3DMC9Fb5mPLIQo9kR&cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&existShop=false&pas=0&cookie14=UoTYPmfqkfjWZQ%3D%3D&tag=8&lng=zh_CN;isg=BLa22BtL9k_FR4Ir6bMwBuFbB-zJtoeaDWeQ6CCfohk0Y1b9iGdKIRyRfz4PTvIp;
