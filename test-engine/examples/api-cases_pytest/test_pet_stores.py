import pytest
import httpx
from conftest import base_url, mock_response


# 测试用例：添加新宠物
@pytest.mark.parametrize("name, photoUrls, expected_status", [
    ("Dog", ["http://example.com/dog.jpg"], 200),
    (None, ["http://example.com/dog.jpg"], 405),
    ("Dog", None, 405)
])
@pytest.mark.asyncio
async def test_add_new_pet(base_url, name, photoUrls, expected_status, api_client):
    url = f"{base_url}/pet"
    payload = {"name": name, "photoUrls": photoUrls}
    response = await api_client.post(url, json=payload)
    assert response.status_code == expected_status


# 测试用例：更新现有宠物
@pytest.mark.parametrize("pet_id, name, photoUrls, expected_status", [
    (1, "Dog", ["http://example.com/dog.jpg"], 200),
    (1, None, ["http://example.com/dog.jpg"], 405),
    (1, "Dog", None, 405),
    ("invalid_id", "Dog", ["http://example.com/dog.jpg"], 400),
    (999999, "Dog", ["http://example.com/dog.jpg"], 404)
])
@pytest.mark.asyncio
async def test_update_pet(base_url, pet_id, name, photoUrls, expected_status, api_client):
    url = f"{base_url}/pet"
    payload = {"id": pet_id, "name": name, "photoUrls": photoUrls}
    response = await api_client.put(url, json=payload)
    assert response.status_code == expected_status


# 测试用例：根据状态查找宠物
@pytest.mark.parametrize("status, expected_status", [
    ("available", 200),
    ("pending", 200),
    ("sold", 200),
    ("invalid_status", 400)
])
@pytest.mark.asyncio
async def test_find_pet_by_status(base_url, status, expected_status, api_client):
    url = f"{base_url}/pet/findByStatus?status={status}"
    response = await api_client.get(url)
    assert response.status_code == expected_status


# 测试用例：根据标签查找宠物
@pytest.mark.parametrize("tags, expected_status", [
    (["tag1"], 200),
    (["invalid_tag"], 400)
])
@pytest.mark.asyncio
async def test_find_pet_by_tags(base_url, tags, expected_status, api_client):
    url = f"{base_url}/pet/findByTags?tags={','.join(tags)}"
    response = await api_client.get(url)
    assert response.status_code == expected_status


# 测试用例：根据ID查找宠物
@pytest.mark.parametrize("pet_id, expected_status", [
    (1, 200),
    ("invalid_id", 400),
    (999999, 404)
])
@pytest.mark.asyncio
async def test_find_pet_by_id(base_url, pet_id, expected_status, api_client):
    url = f"{base_url}/pet/{pet_id}"
    response = await api_client.get(url)
    assert response.status_code == expected_status


# 测试用例：使用表单数据更新宠物
@pytest.mark.parametrize("pet_id, name, status, expected_status", [
    (1, "Dog", "available", 200),
    ("invalid_id", "Dog", "available", 405)
])
@pytest.mark.asyncio
async def test_update_pet_with_form(base_url, pet_id, name, status, expected_status, api_client):
    url = f"{base_url}/pet/{pet_id}"
    payload = {"name": name, "status": status}
    response = await api_client.post(url, data=payload)
    assert response.status_code == expected_status


# 测试用例：删除宠物
@pytest.mark.parametrize("pet_id, expected_status", [
    (1, 200),
    ("invalid_id", 400),
    (999999, 404)
])
@pytest.mark.asyncio
async def test_delete_pet(base_url, pet_id, expected_status, api_client):
    url = f"{base_url}/pet/{pet_id}"
    response = await api_client.delete(url)
    assert response.status_code == expected_status


# 测试用例：上传宠物图片
@pytest.mark.parametrize("pet_id, additionalMetadata, file, expected_status", [
    (1, "metadata", "image.jpg", 200),
    ("invalid_id", "metadata", "image.jpg", 400)
])
@pytest.mark.asyncio
async def test_upload_pet_image(base_url, pet_id, additionalMetadata, file, expected_status, api_client):
    url = f"{base_url}/pet/{pet_id}/uploadImage"
    files = {"file": open(file, "rb")}
    payload = {"additionalMetadata": additionalMetadata}
    response = await api_client.post(url, data=payload, files=files)
    assert response.status_code == expected_status


# 测试用例：获取库存状态
@pytest.mark.asyncio
async def test_get_inventory(base_url, api_client):
    url = f"{base_url}/store/inventory"
    response = await api_client.get(url)
    assert response.status_code == 200


# 测试用例：下订单
@pytest.mark.parametrize("order, expected_status", [
    ({"id": 1, "petId": 1, "quantity": 1, "shipDate": "2023-10-01T00:00:00.000Z", "status": "placed", "complete": True},
     200),
    ({"id": "invalid_id", "petId": 1, "quantity": 1, "shipDate": "2023-10-01T00:00:00.000Z", "status": "placed",
      "complete": True}, 400)
])
@pytest.mark.asyncio
async def test_place_order(base_url, order, expected_status, api_client):
    url = f"{base_url}/store/order"
    response = await api_client.post(url, json=order)
    assert response.status_code == expected_status


# 测试用例：根据ID查找订单
@pytest.mark.parametrize("order_id, expected_status", [
    (1, 200),
    ("invalid_id", 400),
    (999999, 404)
])
@pytest.mark.asyncio
async def test_find_order_by_id(base_url, order_id, expected_status, api_client):
    url = f"{base_url}/store/order/{order_id}"
    response = await api_client.get(url)
    assert response.status_code == expected_status


# 测试用例：删除订单
@pytest.mark.parametrize("order_id, expected_status", [
    (1, 200),
    ("invalid_id", 400),
    (999999, 404)
])
@pytest.mark.asyncio
async def test_delete_order(base_url, order_id, expected_status, api_client):
    url = f"{base_url}/store/order/{order_id}"
    response = await api_client.delete(url)
    assert response.status_code == expected_status


# 测试用例：创建用户
@pytest.mark.parametrize("user, expected_status", [
    ({"id": 1, "username": "testuser", "firstName": "Test", "lastName": "User", "email": "test@example.com",
      "password": "password", "phone": "1234567890", "userStatus": 0}, 200),
    ({"id": "invalid_id", "username": "testuser", "firstName": "Test", "lastName": "User", "email": "test@example.com",
      "password": "password", "phone": "1234567890", "userStatus": 0}, 200)
])
@pytest.mark.asyncio
async def test_create_user(base_url, user, expected_status, api_client):
    url = f"{base_url}/user"
    response = await api_client.post(url, json=user)
    assert response.status_code == expected_status


# 测试用例：使用列表创建用户
@pytest.mark.parametrize("users, expected_status", [
    ([{"id": 1, "username": "testuser1", "firstName": "Test", "lastName": "User", "email": "test1@example.com",
       "password": "password", "phone": "1234567890", "userStatus": 0}], 200),
    ([{"id": "invalid_id", "username": "testuser1", "firstName": "Test", "lastName": "User",
       "email": "test1@example.com", "password": "password", "phone": "1234567890", "userStatus": 0}], 200)
])
@pytest.mark.asyncio
async def test_create_users_with_list(base_url, users, expected_status, api_client):
    url = f"{base_url}/user/createWithList"
    response = await api_client.post(url, json=users)
    assert response.status_code == expected_status


# 测试用例：根据用户名查找用户
@pytest.mark.parametrize("username, expected_status", [
    ("testuser", 200),
    ("invalid_username", 400),
    ("nonexistent_user", 404)
])
@pytest.mark.asyncio
async def test_find_user_by_username(base_url, username, expected_status, api_client):
    url = f"{base_url}/user/{username}"
    response = await api_client.get(url)
    assert response.status_code == expected_status


# 测试用例：更新用户
@pytest.mark.parametrize("username, user, expected_status", [
    ("testuser", {"id": 1, "username": "testuser", "firstName": "Test", "lastName": "User", "email": "test@example.com",
                  "password": "password", "phone": "1234567890", "userStatus": 0}, 200),
    ("invalid_username",
     {"id": 1, "username": "testuser", "firstName": "Test", "lastName": "User", "email": "test@example.com",
      "password": "password", "phone": "1234567890", "userStatus": 0}, 400)
])
@pytest.mark.asyncio
async def test_update_user(base_url, username, user, expected_status, api_client):
    url = f"{base_url}/user/{username}"
    response = await api_client.put(url, json=user)
    assert response.status_code == expected_status
