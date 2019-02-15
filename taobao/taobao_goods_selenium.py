import asyncio
import re
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq

from taobao.taobao_login_getCookies import taoBaoLogin

'''
wait.until()语句是selenum里面的显示等待，wait是一个WebDriverWait对象，它设置了等待时间，如果页面在等待时间内
没有在 DOM中找到元素，将继续等待，超出设定时间后则抛出找不到元素的异常,也可以说程序每隔xx秒看一眼，如果条件
成立了，则执行下一步，否则继续等待，直到超过设置的最长时间，然后抛出TimeoutException
1.presence_of_element_located 元素加载出，传入定位元组，如(By.ID, 'p')
2.element_to_be_clickable 元素可点击
3.text_to_be_present_in_element 某个元素文本包含某文字
'''



def search(keyword,cookie):
    '''
    此函数的作用为完成首页点击搜索的功能，替换标签可用于其他网页使用
    :return:
    '''
    print('正在搜索')
    try:
        #访问页面
        browser.get('https://www.taobao.com')
        browser.delete_all_cookies()
        for res in cookie.split(';')[:-1]:
            u=res.split('=')
            browser.add_cookie({'domain': '.taobao.com', 'httpOnly': False, 'name': u[0], 'path': '/', 'secure': False,'value': u[1], 'expires': None})
        # 选择到淘宝首页的输入框
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        #搜索的那个按钮
        submit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        #send_key作为写到input的内容
        input.send_keys(keyword)
        #执行点击搜索的操作
        submit.click()
        #查看到当前的页码一共是多少页
        total = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        #获取所有的商品
        get_products()
        #返回总页数
        return total.text
    except TimeoutException:
        return search(keyword,cookie)
    # except Exception:
    #     print('cookies可能过期，正在重新获取新的登陆cookies')
    #     cookie = getCookie(username, password)

        # return search(keyword,cookie)


def next_page(page_number):
    '''
    翻页函数，
    :param page_number:
    :return:
    '''
    print('正在翻页', page_number)
    try:
        #这个是我们跳转页的输入框
        input = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        #跳转时的确定按钮
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 '#mainsrp-pager > div > div > div > div.form > span.J_Submit')))
        #清除里面的数字
        input.clear()
        #重新输入数字
        input.send_keys(page_number)
        #选择并点击
        submit.click()
        #判断当前页是不是我们要现实的页
        wait.until(
            EC.text_to_be_present_in_element(
                (By.CSS_SELECTOR,
                 '#mainsrp-pager > div > div > div > ul > li.item.active > span'),
                str(page_number)))
        #调用函数获取商品信息
        get_products()
    #捕捉超时，重新进入翻页的函数
    except TimeoutException:
        next_page(page_number)


def get_products():
    '''
    搜到页面信息在此函数在爬取我们需要的信息
    :return:
    '''
    #每一个商品标签，这里是加载出来以后才会拿网页源代码
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    #这里拿到的是整个网页源代码
    html = browser.page_source
    #pq解析网页源代码
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        # print(item)
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        print(product)


def main():
    try:
            #第一步搜索
        total = search(keyword,cookie)
        #int类型刚才找到的总页数标签，作为跳出循环的条件
        total = int(re.compile('(\d+)').search(total).group(1))
        #只要后面还有就继续爬，继续翻页
        for i in range(2, total+1):
            next_page(i)
            time.sleep(2)   #速度放慢
    except Exception as e:
        print('出错啦',e)
    finally:
        #关闭浏览器
        browser.close()





if __name__ == '__main__':
    username = 'xxxxxx'   #登陆淘宝的账号
    password = 'xxxxxxx'   #登陆密码
    keyword = '美食'     #需要获取的商品关键字
    #第一次登陆
    loop = asyncio.get_event_loop()
    cookie = loop.run_until_complete(taoBaoLogin(username,password))

    print(cookie)
    # 定义一个无界面的浏览器
    browser = webdriver.Chrome(
        service_args=[
            '--load-images=false',
            '--disk-cache=true'])
    # 10s无响应就down掉
    wait = WebDriverWait(browser, 10)
    # 虽然无界面但是必须要定义窗口
    browser.set_window_size(1400, 900)
    main()

