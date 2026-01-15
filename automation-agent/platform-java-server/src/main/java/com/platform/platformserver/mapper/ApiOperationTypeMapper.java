package com.platform.platformserver.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.platform.platformserver.entity.ApiOperationType;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface ApiOperationTypeMapper extends BaseMapper<ApiOperationType> {
}