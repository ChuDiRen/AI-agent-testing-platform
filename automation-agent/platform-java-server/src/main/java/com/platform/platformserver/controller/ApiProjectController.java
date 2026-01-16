package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiProject;
import com.platform.platformserver.service.ApiProjectService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/ApiProject")
public class ApiProjectController {
    
    @Autowired
    private ApiProjectService apiProjectService;
    
    @GetMapping("/queryAll")
    public Result<List<ApiProject>> getProjectList() {
        return apiProjectService.getProjectList();
    }
    
    @GetMapping("/{id}")
    public Result<ApiProject> getProjectById(@PathVariable Long id) {
        return apiProjectService.getProjectById(id);
    }
    
    @PostMapping("/insert")
    public Result<String> insert(@RequestBody ApiProject project) {
        return apiProjectService.createProject(project);
    }
    
    @PutMapping("/update")
    public Result<String> updateProject(@RequestBody ApiProject project) {
        return apiProjectService.updateProject(project);
    }
    
    @DeleteMapping("/delete/{id}")
    public Result<String> deleteProject(@PathVariable Long id) {
        return apiProjectService.deleteProject(id);
    }
}