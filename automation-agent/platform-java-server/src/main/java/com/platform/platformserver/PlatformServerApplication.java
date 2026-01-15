package com.platform.platformserver;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@MapperScan("com.platform.platformserver.mapper")
@EnableAsync
public class PlatformServerApplication {

    public static void main(String[] args) {
        SpringApplication.run(PlatformServerApplication.class, args);
    }
}
