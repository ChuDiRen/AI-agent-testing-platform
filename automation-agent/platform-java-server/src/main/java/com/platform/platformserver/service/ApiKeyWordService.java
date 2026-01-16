package com.platform.platformserver.service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiKeyWord;
import com.platform.platformserver.mapper.ApiKeyWordMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ApiKeyWordService {
    
    @Autowired
    private ApiKeyWordMapper apiKeyWordMapper;
    
    public Result<List<ApiKeyWord>> getKeyWordList(Integer pageId) {
        QueryWrapper<ApiKeyWord> queryWrapper = new QueryWrapper<>();
        if (pageId != null) {
            queryWrapper.eq("page_id", pageId);
        }
        queryWrapper.orderByDesc("id");
        List<ApiKeyWord> keyWordList = apiKeyWordMapper.selectList(queryWrapper);
        return Result.success(keyWordList);
    }
    
    public Result<ApiKeyWord> getKeyWordById(Long id) {
        ApiKeyWord keyWord = apiKeyWordMapper.selectById(id);
        if (keyWord == null) {
            return Result.error("关键字不存在");
        }
        return Result.success(keyWord);
    }
    
    public Result<String> createKeyWord(ApiKeyWord keyWord) {
        apiKeyWordMapper.insert(keyWord);
        return Result.success("关键字创建成功");
    }
    
    public Result<String> updateKeyWord(ApiKeyWord keyWord) {
        apiKeyWordMapper.updateById(keyWord);
        return Result.success("关键字更新成功");
    }
    
    public Result<String> deleteKeyWord(Long id) {
        apiKeyWordMapper.deleteById(id);
        return Result.success("关键字删除成功");
    }
}
