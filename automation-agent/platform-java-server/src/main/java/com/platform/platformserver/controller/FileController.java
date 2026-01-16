package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.service.MinIOService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.util.List;

@RestController
@RequestMapping("/api/v1/file")
public class FileController {
    
    @Autowired
    private MinIOService minIOService;
    
    @PostMapping("/upload")
    public Result<String> uploadFile(@RequestParam("file") MultipartFile file, @RequestParam("objectName") String objectName) {
        try {
            String result = minIOService.uploadFile(objectName, file);
            return Result.success(result);
        } catch (Exception e) {
            return Result.error("文件上传失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/download/{objectName}")
    public Result<InputStream> downloadFile(@PathVariable String objectName) {
        try {
            InputStream inputStream = minIOService.downloadFile(objectName);
            return Result.success(inputStream);
        } catch (Exception e) {
            return Result.error("文件下载失败: " + e.getMessage());
        }
    }
    
    @DeleteMapping("/delete/{objectName}")
    public Result<String> deleteFile(@PathVariable String objectName) {
        try {
            minIOService.deleteFile(objectName);
            return Result.success("文件删除成功");
        } catch (Exception e) {
            return Result.error("文件删除失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/list")
    public Result<List<String>> listFiles() {
        try {
            List<String> fileList = minIOService.listFiles();
            return Result.success(fileList);
        } catch (Exception e) {
            return Result.error("文件列表获取失败: " + e.getMessage());
        }
    }
    
    @GetMapping("/url/{objectName}")
    public Result<String> getFileUrl(@PathVariable String objectName) {
        try {
            String url = minIOService.getFileUrl(objectName);
            return Result.success(url);
        } catch (Exception e) {
            return Result.error("文件URL获取失败: " + e.getMessage());
        }
    }
}