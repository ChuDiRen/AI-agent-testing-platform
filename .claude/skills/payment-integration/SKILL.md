# 支付功能集成技能

## 触发条件
- 关键词：支付、微信支付、支付宝、订单支付、Payment
- 场景：当用户需要集成支付功能时

## 说明

本项目（AI-agent-testing-platform）是 API 测试平台，暂无支付需求。

以下是支付集成的通用规范，供参考。

## 核心规范

### 规范1：支付流程

```
1. 用户下单 → 2. 创建支付订单 → 3. 调用支付接口 → 4. 用户支付
→ 5. 支付回调 → 6. 更新订单状态 → 7. 通知用户
```

### 规范2：订单状态机

```
待支付 → 支付中 → 已支付 → 已完成
                ↘ 支付失败
                ↘ 已取消
                ↘ 已退款
```

### 规范3：安全规范

1. **签名验证** - 所有支付请求必须验签
2. **回调验证** - 验证回调来源和签名
3. **幂等处理** - 回调可能重复，需幂等
4. **金额校验** - 回调金额与订单金额比对
5. **日志记录** - 记录所有支付相关日志

### 规范4：微信支付示例

```python
# 创建支付订单
@router.post("/pay/create")
async def create_payment(order_id: int):
    order = get_order(order_id)
    
    # 调用微信支付 API
    result = wechat_pay.create_order(
        out_trade_no=order.order_no,
        total_fee=order.amount,
        body=order.description,
        notify_url="https://api.example.com/pay/callback"
    )
    
    return respModel.ok_resp(obj=result)

# 支付回调
@router.post("/pay/callback")
async def payment_callback(request: Request):
    # 验证签名
    if not wechat_pay.verify_sign(request):
        return "FAIL"
    
    # 更新订单状态
    order = get_order_by_no(request.out_trade_no)
    if order.status == "待支付":
        order.status = "已支付"
        order.paid_at = datetime.now()
        save_order(order)
    
    return "SUCCESS"
```

### 规范5：前端调起支付

```javascript
// 微信 JSAPI 支付
async function wechatPay(orderId) {
  const res = await api.createPayment(orderId)
  
  WeixinJSBridge.invoke('getBrandWCPayRequest', {
    appId: res.appId,
    timeStamp: res.timeStamp,
    nonceStr: res.nonceStr,
    package: res.package,
    signType: res.signType,
    paySign: res.paySign
  }, (result) => {
    if (result.err_msg === 'get_brand_wcpay_request:ok') {
      // 支付成功
      checkPaymentStatus(orderId)
    }
  })
}
```

## 注意事项

- 支付金额单位通常是分
- 测试环境使用沙箱
- 生产环境密钥妥善保管
- 回调接口必须幂等
