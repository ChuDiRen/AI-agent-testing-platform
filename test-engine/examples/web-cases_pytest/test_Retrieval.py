# -*- coding: utf-8 -*-
"""
@Time ： 2024/03/09 08:30
@Author ：楚地仁人
@File ：test_Retrieval.py
@IDE ：PyCharm
"""
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_chrome_driver():
    """获取配置好的Chrome驱动"""
    chrome_options = Options()
    # 添加一些常用选项
    chrome_options.add_argument('--start-maximized')  # 最大化窗口
    chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
    chrome_options.add_argument('--no-sandbox')  # 禁用沙箱模式
    chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
    
    # 使用webdriver_manager自动下载和管理ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

@allure.title("百度搜索Python测试用例")
def test_01():
    # 初始化Chrome浏览器
    driver = get_chrome_driver()
    try:
        with allure.step("进行百度搜索操作"):
            # 打开百度
            driver.get("https://www.baidu.com")
            
            # 输入搜索关键词
            search_input = driver.find_element(By.ID, "kw")
            search_input.clear()
            search_input.send_keys("Python")
            
            # 点击搜索按钮
            search_btn = driver.find_element(By.ID, "su")
            search_btn.click()
            
            # 等待搜索结果加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "content_left"))
            )
            
            # 验证搜索结果
            page_source = driver.page_source
            assert "Python" in page_source, "搜索结果页面未包含'Python'"
    finally:
        # 关闭浏览器
        driver.quit()

@allure.title("百度搜索Java测试用例")
def test_02():
    # 初始化Chrome浏览器
    driver = get_chrome_driver()
    try:
        with allure.step("进行百度搜索操作"):
            # 打开百度
            driver.get("https://www.baidu.com")
            
            # 输入搜索关键词
            search_input = driver.find_element(By.ID, "kw")
            search_input.clear()
            search_input.send_keys("Java")
            
            # 点击搜索按钮
            search_btn = driver.find_element(By.ID, "su")
            search_btn.click()
            
            # 等待搜索结果加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "content_left"))
            )
            
            # 验证搜索结果
            page_source = driver.page_source
            assert "Java" in page_source, "搜索结果页面未包含'Java'"
    finally:
        # 关闭浏览器
        driver.quit() 