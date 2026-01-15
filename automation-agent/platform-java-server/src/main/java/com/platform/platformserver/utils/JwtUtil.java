package com.platform.platformserver.utils;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.Map;

@Slf4j
@Component
public class JwtUtil {
    
    @Value("${platform.jwt.secret-key}")
    private String secretKey;
    
    @Value("${platform.jwt.expire-minutes}")
    private int expireMinutes;
    
    private SecretKey getSignKey() {
        return Keys.hmacShaKeyFor(secretKey.getBytes(StandardCharsets.UTF_8));
    }
    
    public String generateToken(Long userId, String username, Map<String, Object> claims) {
        Date now = new Date();
        Date expireTime = new Date(now.getTime() + expireMinutes * 60 * 1000L);
        
        JwtBuilder builder = Jwts.builder()
                .subject(String.valueOf(userId))
                .claim("username", username)
                .issuedAt(now)
                .expiration(expireTime)
                .signWith(getSignKey());
        
        if (claims != null && !claims.isEmpty()) {
            claims.forEach(builder::claim);
        }
        
        return builder.compact();
    }
    
    public String generateToken(Long userId, String username) {
        return generateToken(userId, username, null);
    }
    
    public Claims parseToken(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(getSignKey())
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (ExpiredJwtException e) {
            log.error("Token已过期: {}", token);
            throw new RuntimeException("Token已过期");
        } catch (UnsupportedJwtException e) {
            log.error("不支持的Token: {}", token);
            throw new RuntimeException("不支持的Token");
        } catch (MalformedJwtException e) {
            log.error("Token格式错误: {}", token);
            throw new RuntimeException("Token格式错误");
        } catch (IllegalArgumentException e) {
            log.error("Token为空: {}", token);
            throw new RuntimeException("Token为空");
        }
    }
    
    public Long getUserId(String token) {
        Claims claims = parseToken(token);
        return Long.valueOf(claims.getSubject());
    }
    
    public String getUsername(String token) {
        Claims claims = parseToken(token);
        return claims.get("username", String.class);
    }
    
    public boolean validateToken(String token) {
        try {
            parseToken(token);
            return true;
        } catch (Exception e) {
            return false;
        }
    }
    
    public boolean isTokenExpired(String token) {
        try {
            Claims claims = parseToken(token);
            return claims.getExpiration().before(new Date());
        } catch (Exception e) {
            return true;
        }
    }
}
