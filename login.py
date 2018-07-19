from selenium import webdriver
import os


class Login:

    def __init__(self, domain, username, password):
        self.__domain = domain
        self.__username = username
        self.__password = password

    def supplier_login(self):
        browser = self.init_browser()
        browser.get("https://{0}/supplierLogin.html".format(self.__domain))
        print(browser.title)
        print("----准备登录------")
        browser.find_element_by_id("login_account").clear()
        browser.find_element_by_id("login_account").send_keys(self.__username)
        browser.find_element_by_id("login_password").clear()
        browser.find_element_by_id("login_password").send_keys(self.__password)
        browser.find_element_by_id("login").click()
        print("----登录成功------")
        return browser

    def factory_login(self):
        browser = self.init_browser()
        browser.get("https://{0}/login.html".format(self.__domain))
        print(browser.title)
        print("----准备登录------")
        browser.find_element_by_id("username").clear()
        browser.find_element_by_id("username").send_keys(self.__username)
        browser.find_element_by_id("pwd").clear()
        browser.find_element_by_id("pwd").send_keys(self.__password)
        browser.find_element_by_css_selector("input[type=submit]").click()
        print("----登录成功------")
        return browser

    @staticmethod
    def init_browser():
        path = os.path.abspath(__file__)
        driver_path = os.path.join(os.path.dirname(path), 'driver', 'chromedriver.exe')
        options = webdriver.ChromeOptions()
        options.headless = True
        browser = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        browser.implicitly_wait(3)
        browser.maximize_window()
        return browser
