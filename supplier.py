# -*- coding:utf-8 -*-
import configparser
import datetime
import os
import time
from login import Login

from selenium import webdriver


def online_orders():
    navigation_bar('在线接单')
    for order_number in order_numbers:
        order_search('order_number', 'filter_order', order_number)
        if not operation_bar('#order_list'):
            continue
        # 开单页面
        print("----跳转到开单页面--------")
        part_rows = browser.find_elements_by_css_selector('table.orderDetail-table>tbody>tr')
        now = datetime.datetime.now()
        send_time = now + datetime.timedelta(days=1)
        send_time_str = send_time.strftime("%Y-%m-%d %H:%M:%S")
        print("-------填写送货时间------")
        for part in part_rows:
            send_time_input = part.find_element_by_css_selector('td.order-send-time>input')
            send_time_input.clear()
            send_time_input.send_keys(send_time_str)
        print("-------确认开单---------")
        browser.find_element_by_class_name('order-ok').click()
        confirm_click()
        cancel_click()


def operation_bar(table_sign):
    first_row = browser.find_elements_by_css_selector('table{0}>tbody>tr'.format(table_sign))[0]
    first_row_columns = first_row.find_elements_by_tag_name('td')
    if len(first_row_columns) == 1:
        print("------该订单号不存在-----")
        return False
    else:
        print("------开单or打包-----")
        first_row_columns[8].find_element_by_tag_name('a').click()
        return True


def logistics_operation():
    navigation_bar('物流作业')
    for order_number in order_numbers:
        order_search('order-no', 'pack-search', order_number)
        if not operation_bar('.pack-table'):
            continue
        # 打包
        print("----跳转到打包页面--------")
        if unpack == '1':
            part_rows = len(browser.find_elements_by_css_selector('table.pack-table>tbody>tr'))
            for part in range(part_rows):
                first_part = browser.find_elements_by_css_selector('table.pack-table>tbody>tr')[0]
                first_part.find_element_by_css_selector('td.check-box>input[type=checkbox]').click()
                browser.find_element_by_css_selector('button.order-pack').click()
                confirm_click()
                cancel_click()
        else:
            browser.find_element_by_css_selector('input.select-all-parts').click()
            browser.find_element_by_css_selector('button.order-pack').click()
            confirm_click()
            cancel_click()


def order_search(order_number_input_id, search_button_id, order_number):
    print("----开始搜索订单：{0}------".format(order_number))
    browser.find_element_by_id(order_number_input_id).clear()
    browser.find_element_by_id(order_number_input_id).send_keys(order_number)
    browser.find_element_by_id(search_button_id).click()
    print("----订单搜索完成：{0}------".format(order_number))


def navigation_bar(title):
    print("----导航栏定位中：{0}------".format(title))
    links = browser.find_elements_by_css_selector('div#header>div.on-right>div.links>a')
    for link in links:
        if link.text == title:
            link.click()
            break


def confirm_click():
    print("--------确定--------")
    ok_button = browser.find_element_by_css_selector('button[i-id=ok]')
    browser.execute_script("arguments[0].click();", ok_button)


def cancel_click():
    print("--------不打印--------")
    time.sleep(3)
    not_print_button = browser.find_element_by_css_selector('button[i-id=cancel]')
    browser.execute_script("arguments[0].click();", not_print_button)


if __name__ == '__main__':
    path = os.path.abspath(__file__)
    conf = configparser.ConfigParser()
    conf.read(os.path.join(os.path.dirname(path), 'config', 'config.ini'), encoding='utf-8')
    # chrome_driver = conf.get('main', 'driver')
    domain = conf.get('supplier', 'domain')
    username = conf.get('supplier', 'username')
    password = conf.get('supplier', 'password')

    order_numbers = str(conf.get('supplier', 'order_number')).split(',')
    unpack = conf.get('supplier', 'unpack')

    # options = webdriver.ChromeOptions()
    # options.headless = True
    # browser = webdriver.Chrome(executable_path=chrome_driver, chrome_options=options)
    # browser.maximize_window()

    # 登录
    # browser.get("https://{0}/supplierLogin.html".format(domain))
    # print(browser.title)
    # print("----准备登录------")
    # browser.find_element_by_id("login_account").clear()
    # browser.find_element_by_id("login_account").send_keys(username)
    # browser.find_element_by_id("login_password").clear()
    # browser.find_element_by_id("login_password").send_keys(password)
    # browser.find_element_by_id("login").click()
    # print("----登录成功------")

    login = Login(domain, username, password)
    browser = login.supplier_login()

    online_orders()
    logistics_operation()
    print("---------任务完成，退出---------")
    browser.quit()
