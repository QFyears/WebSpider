# -*- coding:utf-8 -*-

from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from chaojiying import Chaojiying
from utils.config import *
from utils.handle import handle_code
import time

class Login_Cnki(object):
    def __init__(self, code=None):
        """
        初始化注册信息
        :param code: 验证码
        """
        self.url = URL  # 目标站点
        self.browser = webdriver.Chrome()       # 声明浏览器对象
        self.browser.get(self.url)              # 访问网页
        self.wait = WebDriverWait(self.browser, 5)    # 显式等待5秒，待节点元素全部加载
        self.username = USERNAME    # 用户名
        self.password = PASSWORD    # 密码
        self.email = EMAIL          # 邮箱
        self.code = code            # 图形验证码
        self.chaojiying = Chaojiying(CHAIJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAIJIYING_SOFT_ID)  # 创建超级鹰对象

    def __del__(self):
        self.browser.close()

    def get_position(self):
        """
        获取验证码位置
        :return: 验证码位置元组
        """
        img = self.wait.until(EC.presence_of_element_located((By.ID, 'checkcode')))     # 获取图形验证码的节点
        time.sleep(2)
        location = img.location     # 获取图形验证码在网页中的相对位置
        size = img.size             # 获取图形验证码的大小
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']                # 分别获取左上角和右下角的坐标
        return [top, bottom, left, right]     # 返回坐标

    def get_screenshot(self):
        """
        获取网页截图
        :return: 截图对象
        """
        screenshot = self.browser.get_screenshot_as_png()   # 获取网页的PNG格式截图
        screenshot = Image.open(BytesIO(screenshot))    # 创建Image对象
        return screenshot

    def get_geetest_image(self, name='code.png'):
        """
        获取验证码图片
        :return: 图片对象
        """
        top, bottom, left, right = self.get_position()      # 获取坐标点
        print('验证码位置：', top, bottom, left, right)
        screenshot = self.get_screenshot()  # 获取网页截图
        captcha = screenshot.crop((left, top, right, bottom))   # 将二维码从网页截图中裁剪下来
        captcha.save(name)      # 存储为'code.png'
        return captcha          # 返回Image对象

    def get(self):
        """
        获取注册信息输入框节点
        :return:
        """
        # 若"立即注册"按钮加载完毕,认为各节点加载完毕.
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, 'ButtonRegister')))
        except TimeoutException:
            pass
        input_username = self.browser.find_element_by_id('username')        # 获取用户名输入框
        input_password = self.browser.find_element_by_id('txtPassword')     # 获取密码输入框
        input_email = self.browser.find_element_by_id('txtEmail')           # 获取邮箱输入框
        input_code = self.browser.find_element_by_id('txtOldCheckCode')     # 获取验证码输入框
        register = self.browser.find_element_by_id('ButtonRegister')        # 获取注册按钮
        return [input_username, input_password, input_email, input_code, register]

    def get_result(self, image):
        """
        获取超级鹰返回的结果
        :param image: 验证码的Image对象
        :return: 识别结果
        """
        bytes_array = BytesIO() # 创建一个BytesIO类型的字节数组
        image.save(bytes_array, format='PNG')   # 写入验证码的二进制流
        # 识别验证码
        captcha_result = self.chaojiying.PostPic(bytes_array.getvalue(), CHAOJIYING_KIND)   # 发送至超级鹰识别验证
        result = captcha_result.get('pic_str')  # 获取识别结果
        return result

    def login(self):
        """
        注册登录知网
        :return:
        """
        print('正在获取图形验证码...')
        # _, res_2 = handle_code(self.get_geetest_image())        # 返回结果为两个,可任意选取一种结果(你认为识别精度比较高的那一个)
        # self.code = _   # 赋值任意一个code
        self.code = self.get_result(self.get_geetest_image())
        username, password, email, code, register = self.get()  # 获取节点
        username.send_keys(self.username)   # 输入用户名
        time.sleep(2)
        password.send_keys(self.password)   # 输入密码
        time.sleep(2)
        email.send_keys(self.email)         # 输入邮箱
        time.sleep(2)
        code.send_keys(self.code)           # 输入验证码
        time.sleep(2)
        register.click()  # 注册
        time.sleep(3)
        print('注册成功!')

if __name__ == '__main__':
    Login = Login_Cnki()
    Login.login()
