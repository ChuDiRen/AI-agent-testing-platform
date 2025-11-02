# -*- coding: utf-8 -*-
"""
@Time ： 2024/10/20 下午8:50
@Author ：楚地仁人
@File ：test_petstore.py.py
@IDE ：PyCharm

"""
import pytest
from conftest import keyWords, BASE_URL, pet_id


@pytest.mark.asyncio
async def test_create_pet(pet_id):
    # 测试创建宠物
    url = f"{BASE_URL}/pet/{pet_id}"
    response = await keyWords.request_get_row(url=url)
    assert response.status_code == 200
    assert response.json()['name'] == "Fluffy"


@pytest.mark.asyncio
async def test_update_pet(pet_id):
    # 测试更新宠物
    url = f"{BASE_URL}/pet"
    payload = {
        "id": pet_id,
        "name": "Fluffy II",
        "category": {
            "id": 1,
            "name": "Dogs"
        },
        "photoUrls": [
            "http://example.com/fluffy2.jpg"
        ],
        "tags": [
            {
                "id": 1,
                "name": "cute"
            }
        ],
        "status": "sold"
    }
    response = await keyWords.request_put_row(url=url, json=payload)
    assert response.status_code == 200

    # 验证更新后的宠物信息
    url = f"{BASE_URL}/pet/{pet_id}"
    response = await keyWords.request_get_row(url=url)
    assert response.status_code == 200
    assert response.json()['name'] == "Fluffy II"
    assert response.json()['status'] == "sold"


@pytest.mark.asyncio
async def test_delete_pet(pet_id):
    # 测试删除宠物
    url = f"{BASE_URL}/pet/{pet_id}"
    response = await keyWords.request_delete_row(url=url)
    assert response.status_code == 200

    # 验证宠物是否已被删除
    response = await keyWords.request_get_row(url=url)
    assert response.status_code == 404
