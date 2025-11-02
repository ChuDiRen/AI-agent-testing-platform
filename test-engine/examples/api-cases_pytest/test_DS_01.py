# -*- coding: utf-8 -*-
"""
@Time ： 2024/10/23 下午11:28
@Author ：楚地仁人
@File ：test_DS_01.py
@IDE ：PyCharm

"""
import pytest
import allure
from conftest import keyWords, process_request_data

from testengine_api.core.globalContext import g_context


@allure.title("DS_02 登录成功测试用例")
@pytest.mark.asyncio
async def test_01():
    with allure.step("进行登录操作"):
        url = "http://shop-xo.hctestedu.com/index.php?s=/api/user/login&application=app"
        header = {"content-type": "application/x-www-form-urlencoded"}
        data = {
            "accounts": "lisi",
            "pwd": "123456",
            "type": "username"
        }
        request_data = {"url": url, "headers": header, "data": data}
        request_data = process_request_data(request_data)
        await keyWords.request_post_row(**request_data)
        keyWords.ex_jsonData(EXVALUE="$..token", VARNAME="token")
