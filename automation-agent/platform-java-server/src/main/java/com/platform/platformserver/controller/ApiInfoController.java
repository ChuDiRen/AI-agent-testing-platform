package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfo;
import com.platform.platformserver.service.ApiInfoService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiInfo")
public class ApiInfoController {
    
    @Autowired
    private ApiInfoService apiInfoService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiInfo>> getApiInfoList(@RequestParam(required = false) Long projectId) {
        return apiInfoService.getApiInfoList(projectId);
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(required = false) Integer page,
            @RequestParam(required = false) Integer page_size,
            @RequestParam(required = false) Long project_id,
            @RequestParam(required = false) Long module_id,
            @RequestParam(required = false) String api_name) {
        return apiInfoService.queryByPage(page, page_size, project_id, module_id, api_name);
    }
    
    @GetMapping("/queryById")
    public Result<ApiInfo> queryById(@RequestParam Long id) {
        return apiInfoService.queryById(id);
    }
    
    @PostMapping("/insert")
    public Result<Map<String, Object>> insert(@RequestBody ApiInfo apiInfo) {
        return apiInfoService.insert(apiInfo);
    }
    
    @PutMapping("/update")
    public Result<String> update(@RequestParam Long id, @RequestBody ApiInfo apiInfo) {
        return apiInfoService.update(id, apiInfo);
    }
    
    @DeleteMapping("/delete")
    public Result<String> delete(@RequestParam Long id) {
        return apiInfoService.delete(id);
    }
    
    @PostMapping("/swagger_import")
    public Result<Map<String, Object>> swaggerImport(
            @RequestParam("file") MultipartFile file,
            @RequestParam(required = false) Long project_id) {
        return apiInfoService.swaggerImport(file, project_id);
    }
    
    @PostMapping("/debug")
    public Result<Map<String, Object>> debugExecute(
            @RequestParam Long id,
            @RequestParam(required = false, defaultValue = "false") Boolean download_response) {
        return apiInfoService.debugExecute(id, download_response);
    }
}