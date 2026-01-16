package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.User;
import com.platform.platformserver.service.UserService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@Tag(name = "登录", description = "用户登录相关接口")
public class LoginController {
    
    private final UserService userService;
    
    @PostMapping("/login")
    @Operation(summary = "用户登录", description = "用户登录接口，返回JWT Token")
    public Result<Map<String, Object>> login(@RequestParam String username, @RequestParam String password) {
        log.info("用户登录请求: username={}", username);
        
        try {
            Result<Map<String, Object>> loginResult = userService.login(username, password);
            
            if (loginResult.getCode() == 200) {
                Map<String, Object> responseData = new HashMap<>();
                Map<String, Object> data = loginResult.getData();
                
                // 构建用户信息
                User user = (User) data.get("user");
                Map<String, Object> userInfo = new HashMap<>();
                userInfo.put("id", user.getId());
                userInfo.put("username", user.getUsername());
                userInfo.put("create_time", user.getCreateTime() != null ? 
                    user.getCreateTime().toString() : "");
                
                // 构建响应数据，与FastAPI格式一致
                responseData.put("code", 200);
                responseData.put("msg", "登录成功");
                responseData.put("data", userInfo);
                responseData.put("token", data.get("token"));
                
                return Result.success(responseData);
            } else {
                return loginResult;
            }
        } catch (Exception e) {
            log.error("登录失败: {}", e.getMessage());
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("code", 401);
            errorResponse.put("msg", "登录失败: " + e.getMessage());
            errorResponse.put("data", null);
            return Result.error(401, "登录失败: " + e.getMessage());
        }
    }
}
