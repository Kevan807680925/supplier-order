# -*- coding:utf-8 -*-
import configparser
import datetime
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from login import Login


class SupplierPack:
    browser = None

    def __init__(self):
        path = os.path.abspath(__file__)
        conf = configparser.ConfigParser()
        conf.read(os.path.join(os.path.dirname(path), 'config', 'config.ini'), encoding='utf-8')
        self.__domain = conf.get('supplier', 'domain')
        self.__username = conf.get('supplier', 'username')
        self.__password = conf.get('supplier', 'password')

    def online_orders(self, order_numbers):
        self.navigation_bar('在线接单')
        for order_number in order_numbers:
            self.order_search('order_number', 'filter_order', order_number)
            if not self.operation_bar('#order_list'):
                continue
            # 开单页面
            print("----跳转到开单页面--------")
            part_rows = self.browser.find_elements_by_css_selector('table.orderDetail-table>tbody>tr')
            now = datetime.datetime.now()
            send_time = now + datetime.timedelta(days=1)
            send_time_str = send_time.strftime("%Y-%m-%d %H:%M:%S")
            print("-------填写送货时间------")
            for part in part_rows:
                send_time_input = part.find_element_by_css_selector('td.order-send-time>input')
                send_time_input.clear()
                send_time_input.send_keys(send_time_str)
            print("-------确认开单---------")
            self.browser.find_element_by_class_name('order-ok').click()
            self.confirm_click()
            self.cancel_click()

    def operation_bar(self, table_sign):
        first_row = self.browser.find_elements_by_css_selector('table{0}>tbody>tr'.format(table_sign))[0]
        first_row_columns = first_row.find_elements_by_tag_name('td')
        if len(first_row_columns) == 1:
            print("------该订单号不存在-----")
            return False
        else:
            print("------开单or打包-----")
            first_row_columns[8].find_element_by_tag_name('a').click()
            return True

    def order_search(self, order_number_input_id, search_button_id, order_number):
        print("----开始搜索订单：{0}------".format(order_number))
        self.browser.find_element_by_id(order_number_input_id).clear()
        self.browser.find_element_by_id(order_number_input_id).send_keys(order_number)
        self.browser.find_element_by_id(search_button_id).click()
        print("----订单搜索完成：{0}------".format(order_number))

    def navigation_bar(self, title):
        print("----导航栏定位中：{0}------".format(title))
        links = self.browser.find_elements_by_css_selector('div#header>div.on-right>div.links>a')
        for link in links:
            if link.text == title:
                link.click()
                break

    def confirm_click(self):
        print("--------确定--------")
        WebDriverWait(self.browser, 3, 0.2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[i-id=ok]')))
        ok_button = self.browser.find_element_by_css_selector('button[i-id=ok]')
        self.browser.execute_script("arguments[0].click();", ok_button)

    def cancel_click(self):
        print("--------不打印--------")
        WebDriverWait(self.browser, 3, 0.2).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[i-id=cancel]')))
        not_print_button = self.browser.find_element_by_css_selector('button[i-id=cancel]')
        self.browser.execute_script("arguments[0].click();", not_print_button)

    def logistics_operation(self, order_numbers, unpack):
        self.navigation_bar('物流作业')
        for order_number in order_numbers:
            self.order_search('order-no', 'pack-search', order_number)
            if not self.operation_bar('.pack-table'):
                continue
            # 打包
            print("----跳转到打包页面--------")
            if unpack == '1':
                part_rows = len(self.browser.find_elements_by_css_selector('table.pack-table>tbody>tr'))
                for part in range(part_rows):
                    first_part = self.browser.find_elements_by_css_selector('table.pack-table>tbody>tr')[0]
                    first_part.find_element_by_css_selector('td.check-box>input[type=checkbox]').click()
                    self.browser.find_element_by_css_selector('button.order-pack').click()
                    self.confirm_click()
                    self.cancel_click()
            else:
                self.browser.find_element_by_css_selector('input.select-all-parts').click()
                self.browser.find_element_by_css_selector('button.order-pack').click()
                self.confirm_click()
                self.cancel_click()

    def pack(self, order_numbers, unpack):
        login = Login(self.__domain, self.__username, self.__password)
        self.browser = login.supplier_login()
        self.online_orders(order_numbers)
        self.logistics_operation(order_numbers, unpack)
        print("---------任务完成，退出---------")
        self.browser.quit()


if __name__ == '__main__':
    path = os.path.abspath(__file__)
    conf = configparser.ConfigParser()
    conf.read(os.path.join(os.path.dirname(path), 'config', 'config.ini'), encoding='utf-8')
    order_numbers = str(conf.get('supplier', 'order_number')).split(',')
    unpack = conf.get('supplier', 'unpack')
    SupplierPack().pack(order_numbers, unpack)
