import os
import time
from login import Login
import configparser
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from supplier import SupplierPack
import random


class FactoryOrder:
    __browser = None

    def __init__(self):
        path = os.path.abspath(__file__)
        conf = configparser.ConfigParser()
        conf.read(os.path.join(os.path.dirname(path), 'config', 'config.ini'), encoding='utf-8')
        self.__domain = conf.get('factory', 'domain')
        self.__username = conf.get('factory', 'username')
        self.__password = conf.get('factory', 'password')

        self.__inquiry_nos = str(conf.get('factory', 'inquiry_no')).split(',')
        self.__unpack = conf.get('factory', 'unpack')
        self.__parts_maximum = int(conf.get('factory', 'parts_maximum'))

    def _navigate(self):
        print("----导航栏定位中：询价结果------")
        a_links = self.__browser.find_elements_by_css_selector('a.nav-link')
        for link in a_links:
            if link.text == '询价结果':
                link.click()
                break

    def _is_continue(self, list_body, inquiry_no):
        if len(list_body) == 0:
            print("询价单{0}不存在".format(inquiry_no))
            return False
        if list_body[0].find_element_by_css_selector('ul>li.status').text != '已报价':
            print("询价单{0}报价未完成".format(inquiry_no))
            return False
        return True

    def order(self):
        order_nos = []
        login = Login(self.__domain, self.__username, self.__password)
        self.__browser = login.factory_login()
        self._close_floating_layer()
        self._navigate()
        for inquiry_no in self.__inquiry_nos:
            self.inquiry_no_search(inquiry_no)
            list_body = self.__browser.find_elements_by_css_selector('div.list-body>div')
            if not self._is_continue(list_body, inquiry_no):
                continue
            # 点击详情
            list_body[0].find_element_by_css_selector('ul>li.operate>a').click()
            print("--------报价详情页-----")
            handles = self.__browser.window_handles
            # 切换至详情页继续操作
            self.__browser.switch_to_window(handles[1])
            self._add_parts_to_shopping_cat()
            self._shopping_car_page()
            self._submit_order()
            self._get_order_no(order_nos)
            self._use_qpb_pay()
            # 切换到第一个窗口
            self.__browser.switch_to_window(handles[0])
            self._navigate()
        self.__browser.quit()
        SupplierPack().pack(order_nos, self.__unpack)
        print("---------任务完成，退出---------")

    def _use_qpb_pay(self):
        WebDriverWait(self.__browser, 10, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'label[for=use_qpb]')))
        use_qpb_pay_btn = self.__browser.find_element_by_css_selector('label[for=use_qpb]')
        ActionChains(self.__browser).click(use_qpb_pay_btn).perform()
        ensure_pay_btn = self.__browser.find_element_by_css_selector('div.ensurePay')
        ActionChains(self.__browser).click(ensure_pay_btn).perform()

    def _get_order_no(self, order_nos):
        print("------------支付页-----------")
        WebDriverWait(self.__browser, 10, 0.5).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'span.orderNo'), '订单号：O'))
        order_no_str = self.__browser.find_element_by_css_selector('span.orderNo').text
        order_no = order_no_str[4:]
        print("----订单号：{0}------".format(order_no))
        order_nos.append(order_no)

    def _submit_order(self):
        print("-----------结算页---------------")
        WebDriverWait(self.__browser, 10, 0.5).until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'div.submit_btn'), '提交订单'))
        self.__browser.find_element_by_css_selector('div.submit_btn').click()

    def _shopping_car_page(self):
        print("------------购物车------------")
        WebDriverWait(self.__browser, 10, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'part_list')))
        print("购物车中有{0}件配件".format(len(self.__browser.find_elements_by_css_selector('div.part_list>div'))))
        quantity_inputs = self.__browser.find_elements_by_css_selector('li.quantity>input')
        for i in range(len(quantity_inputs)):
            quantity = random.randint(1, self.__parts_maximum)
            ActionChains(self.__browser).move_to_element(self.__browser.find_elements_by_css_selector('li.quantity>input')[i]).click().send_keys(quantity).perform()
            time.sleep(1)
        select_all_btn = self.__browser.find_element_by_css_selector('label[for=select-all-checkbox1]')
        self.__browser.execute_script("arguments[0].click();", select_all_btn)
        self.__browser.find_element_by_css_selector('li.go-checkout').click()

    def _add_parts_to_shopping_cat(self):
        add_button_selector = (By.CSS_SELECTOR, 'div.td-shoppingCar>span.js-addToShoppingCar')
        WebDriverWait(self.__browser, 10, 0.5).until(EC.presence_of_element_located(add_button_selector))
        add_buttons = self.__browser.find_elements(add_button_selector[0], add_button_selector[1])
        print('-----配件数量：{0}-----'.format(len(add_buttons)))
        for add_button in add_buttons:
            self.__browser.execute_script("arguments[0].click();", add_button)
            try:
                WebDriverWait(self.__browser, 1, 0.2).until(EC.text_to_be_present_in_element(add_button_selector, '已加入'))
                print('已添加1个配件至购物车')
            except TimeoutException:
                try:
                    WebDriverWait(self.__browser, 1, 0.2).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'button[i-id=cancel]')))
                    not_print_button = self.__browser.find_element_by_css_selector('button[i-id=cancel]')
                    self.__browser.execute_script("arguments[0].click();", not_print_button)
                except TimeoutException as e:
                    print(e)
        shopping_car_btn = self.__browser.find_element_by_css_selector('div#shoppingCarBtn>a')
        self.__browser.execute_script("arguments[0].click();", shopping_car_btn)

    def inquiry_no_search(self, inquiry_no):
        inquiry_no_input = self.__browser.find_element_by_css_selector('input[name=inquiryNo]')
        inquiry_no_input.clear()
        inquiry_no_input.send_keys(inquiry_no)
        self.__browser.find_element_by_css_selector('button.btn-search').click()

    def _close_floating_layer(self):
        print("关闭弹窗----------------")
        WebDriverWait(self.__browser, 5, 0.5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.content>a.btn-close')))
        self.__browser.find_element_by_css_selector('div.content>a.btn-close').click()


if __name__ == '__main__':
    FactoryOrder().order()
