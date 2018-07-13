import os
from selenium import webdriver
import configparser


if __name__ == '__main__':
    path = os.path.abspath(__file__)
    conf = configparser.ConfigParser()
    conf.read(os.path.join(os.path.dirname(path), 'config.ini'), encoding='utf-8')
    chrome_driver = conf.get('main', 'driver')
    domain = conf.get('main', 'domain')
    username = conf.get('main', 'username')
    password = conf.get('main', 'password')

    order_numbers = str(conf.get('data', 'order_number')).split(',')
    unpack = conf.get('data', 'unpack')

    options = webdriver.ChromeOptions()
    options.headless = True
    browser = webdriver.Chrome(executable_path=chrome_driver, chrome_options=options)
    browser.maximize_window()

    browser.get("https://{0}/supplierLogin.html".format(domain))