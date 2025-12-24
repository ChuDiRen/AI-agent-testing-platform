# 微信生态集成技能

## 触发条件
- 关键词：微信、公众号、小程序登录、分享、JSSDK、微信生态
- 场景：当用户需要集成微信相关功能时

## 说明

本项目（AI-agent-testing-platform）是 API 测试平台，暂无微信集成需求。

以下是微信集成的通用规范，供参考。

## 核心规范

### 规范1：微信登录流程

```
1. 前端获取 code → 2. 后端换取 access_token 
→ 3. 获取用户信息 → 4. 创建/关联用户 → 5. 返回 JWT Token
```

### 规范2：后端微信登录

```python
import httpx

@router.post("/auth/wechat")
async def wechat_login(code: str):
    # 1. 用 code 换取 access_token
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.weixin.qq.com/sns/oauth2/access_token",
            params={
                "appid": settings.WECHAT_APP_ID,
                "secret": settings.WECHAT_APP_SECRET,
                "code": code,
                "grant_type": "authorization_code"
            }
        )
        data = resp.json()
    
    if "errcode" in data:
        return respModel.error_resp(data["errmsg"])
    
    # 2. 获取用户信息
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.weixin.qq.com/sns/userinfo",
            params={
                "access_token": data["access_token"],
                "openid": data["openid"]
            }
        )
        user_info = resp.json()
    
    # 3. 创建或关联用户
    user = find_or_create_user(user_info)
    
    # 4. 返回 Token
    token = create_token({"user_id": user.id})
    return respModel.ok_resp(obj={"token": token})
```

### 规范3：JSSDK 配置

```python
import hashlib
import time
import random
import string

@router.get("/wechat/jsconfig")
async def get_js_config(url: str):
    # 获取 jsapi_ticket
    ticket = await get_jsapi_ticket()
    
    # 生成签名
    noncestr = ''.join(random.choices(string.ascii_letters, k=16))
    timestamp = int(time.time())
    
    sign_str = f"jsapi_ticket={ticket}&noncestr={noncestr}&timestamp={timestamp}&url={url}"
    signature = hashlib.sha1(sign_str.encode()).hexdigest()
    
    return respModel.ok_resp(obj={
        "appId": settings.WECHAT_APP_ID,
        "timestamp": timestamp,
        "nonceStr": noncestr,
        "signature": signature
    })
```

### 规范4：前端 JSSDK 使用

```javascript
// 初始化 JSSDK
async function initWechatSDK() {
  const config = await api.getJsConfig(window.location.href)
  
  wx.config({
    debug: false,
    appId: config.appId,
    timestamp: config.timestamp,
    nonceStr: config.nonceStr,
    signature: config.signature,
    jsApiList: ['updateAppMessageShareData', 'updateTimelineShareData']
  })
  
  wx.ready(() => {
    // 配置分享
    wx.updateAppMessageShareData({
      title: '分享标题',
      desc: '分享描述',
      link: window.location.href,
      imgUrl: 'https://example.com/share.png'
    })
  })
}
```

### 规范5：小程序登录

```javascript
// 小程序端
wx.login({
  success: async (res) => {
    if (res.code) {
      // 发送 code 到后端
      const result = await api.miniLogin(res.code)
      // 保存 token
      wx.setStorageSync('token', result.token)
    }
  }
})
```

## 注意事项

- AppID 和 Secret 不要暴露到前端
- access_token 需要缓存，有调用频率限制
- 测试环境配置测试号
- 生产环境需要认证服务号
