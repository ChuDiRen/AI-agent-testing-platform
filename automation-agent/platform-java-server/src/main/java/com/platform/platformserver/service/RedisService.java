package com.platform.platformserver.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Service
public class RedisService {
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    public void set(String key, Object value, long timeout, TimeUnit unit) {
        redisTemplate.opsForValue().set(key, value, timeout, unit);
    }
    
    public void set(String key, Object value) {
        redisTemplate.opsForValue().set(key, value);
    }
    
    public Object get(String key) {
        return redisTemplate.opsForValue().get(key);
    }
    
    public boolean delete(String key) {
        return redisTemplate.delete(key);
    }
    
    public boolean hasKey(String key) {
        return redisTemplate.hasKey(key);
    }
    
    public void setExpire(String key, long timeout, TimeUnit unit) {
        redisTemplate.expire(key, timeout, unit);
    }
    
    public Long getExpire(String key) {
        return redisTemplate.getExpire(key);
    }
}