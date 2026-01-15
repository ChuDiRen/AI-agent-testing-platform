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

@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    @Autowired
    private JwtUtil jwtUtil;
    
    public Result<String> login(String username, String password) {
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
        return Result.success(token);
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