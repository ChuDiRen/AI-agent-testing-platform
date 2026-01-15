package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.User;
import com.platform.platformserver.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @PostMapping("/login")
    public Result<String> login(@RequestParam String username, @RequestParam String password) {
        return userService.login(username, password);
    }
    
    @PostMapping("/register")
    public Result<String> register(@RequestBody User user) {
        return userService.register(user);
    }
}