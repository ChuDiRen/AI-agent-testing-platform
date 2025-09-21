---
description: 
globs: src/api/*.js
alwaysApply: false
---
#说明
本规则适用于所有需要调用api请求的功能
#项目结构
- api目录存放所有跟后端请求的服务API，任何涉及到后端调用的必须卸载这个目录里面
- api的命名方式 模块名称大写API.js
- 每个接口必须有注释，注释格式如下：
/**
* 接口名称
* 功能描述
* 入参
* 返回参数
* url地址
* 请求方式
**/
- 每个接口的实现可参考如下示例：
    import { get, post, put, del } from './index.js'
    /**
    * 获取购物车列表
    * 功能描述：获取用户购物车中的所有商品
    * 入参：无
    * 返回参数：购物车商品列表
    * url地址：/cart/list
    * 请求方式：GET
    */
    export function getCartList() {    
        return get('/cart/list')
    }

