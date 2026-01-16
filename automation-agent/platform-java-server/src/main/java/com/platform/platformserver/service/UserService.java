package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.User;
import com.platform.platformserver.exception.BusinessException;
import com.platform.platformserver.mapper.UserMapper;
import com.platform.platformserver.utils.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.util.DigestUtils;

import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;

@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    public Result<Map<String, Object>> login(String username, String password) {
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("username", username);
        User user = userMapper.selectOne(queryWrapper);
        
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        
        String md5Password = DigestUtils.md5DigestAsHex(password.getBytes());
        if (!user.getPassword().equals(md5Password)) {
            throw new BusinessException("密码错误");
        }
        
        String token = jwtUtil.generateToken(user.getId(), user.getUsername());
        
        Map<String, Object> userData = new HashMap<>();
        userData.put("id", user.getId());
        userData.put("username", user.getUsername());
        userData.put("create_time", user.getCreateTime() != null ? 
            user.getCreateTime().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) : "");
        
        Map<String, Object> resultData = new HashMap<>();
        resultData.put("data", userData);
        resultData.put("token", token);
        
        return Result.success(resultData, "登录成功");
    }
    
    public Result<String> register(User user) {
        QueryWrapper<User> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("username", user.getUsername());
        User existingUser = userMapper.selectOne(queryWrapper);
        
        if (existingUser != null) {
            throw new BusinessException("用户名已存在");
        }
        
        String md5Password = DigestUtils.md5DigestAsHex(user.getPassword().getBytes());
        user.setPassword(md5Password);
        userMapper.insert(user);
        
        return Result.success("注册成功");
    }
    
    public User getUserById(Long id) {
        return userMapper.selectById(id);
    }
}