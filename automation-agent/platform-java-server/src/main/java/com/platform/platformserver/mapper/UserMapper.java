package com.platform.platformserver.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.platform.platformserver.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
}