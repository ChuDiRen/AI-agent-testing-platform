package com.platform.platformserver.interceptor;

import com.platform.platformserver.common.ResultCode;
import com.platform.platformserver.exception.BusinessException;
import com.platform.platformserver.utils.JwtUtil;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Slf4j
@Component
@RequiredArgsConstructor
public class JwtInterceptor implements HandlerInterceptor {
    
    private final JwtUtil jwtUtil;
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 从token字段获取Token（与FastAPI保持一致）
        String token = request.getHeader("token");
        
        if (token == null || token.isEmpty()) {
            throw new BusinessException(ResultCode.UNAUTHORIZED);
        }
        
        if (!jwtUtil.validateToken(token)) {
            throw new BusinessException(ResultCode.TOKEN_INVALID);
        }
        
        if (jwtUtil.isTokenExpired(token)) {
            throw new BusinessException(ResultCode.TOKEN_EXPIRED);
        }
        
        Long userId = jwtUtil.getUserId(token);
        String username = jwtUtil.getUsername(token);
        
        request.setAttribute("userId", userId);
        request.setAttribute("username", username);
        
        log.debug("用户验证成功: userId={}, username={}", userId, username);
        
        return true;
    }
}
