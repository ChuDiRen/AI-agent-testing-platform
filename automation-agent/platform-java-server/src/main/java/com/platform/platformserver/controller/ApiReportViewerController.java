package com.platform.platformserver.controller;

import com.platform.platformserver.common.Result;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/v1/ApiReportViewer")
public class ApiReportViewerController {
    
    @GetMapping("/queryAll")
    public Result<List<Map<String, Object>>> queryAll() {
        List<Map<String, Object>> reports = List.of(
            Map.of(
                "id", 1,
                "report_name", "API测试报告_2024-01-01",
                "project_id", 1,
                "test_suite_name", "用户管理测试套件",
                "total_cases", 100,
                "passed_cases", 85,
                "failed_cases", 15,
                "execution_time", "2024-01-01 10:00:00",
                "status", "completed"
            ),
            Map.of(
                "id", 2,
                "report_name", "API测试报告_2024-01-02",
                "project_id", 1,
                "test_suite_name", "订单管理测试套件",
                "total_cases", 50,
                "passed_cases", 45,
                "failed_cases", 5,
                "execution_time", "2024-01-02 14:30:00",
                "status", "completed"
            )
        );
        return Result.success("查询成功", reports);
    }
    
    @PostMapping("/queryByPage")
    public Result<Map<String, Object>> queryByPage(
            @RequestParam(defaultValue = "1") Integer page,
            @RequestParam(defaultValue = "10") Integer pageSize,
            @RequestParam(required = false) Long projectId,
            @RequestParam(required = false) String reportName
    ) {
        List<Map<String, Object>> reports = List.of(
            Map.of(
                "id", 1,
                "report_name", "API测试报告_2024-01-01",
                "project_id", 1,
                "test_suite_name", "用户管理测试套件",
                "total_cases", 100,
                "passed_cases", 85,
                "failed_cases", 15,
                "execution_time", "2024-01-01 10:00:00",
                "status", "completed"
            )
        );
        return Result.success(Map.of(
            "list", reports,
            "total", 1
        ));
    }
    
    @GetMapping("/queryById")
    public Result<Map<String, Object>> queryById(@RequestParam Long id) {
        Map<String, Object> reportDetail = Map.of(
            "id", id,
            "report_name", "API测试报告_2024-01-01",
            "project_id", 1,
            "test_suite_name", "用户管理测试套件",
            "total_cases", 100,
            "passed_cases", 85,
            "failed_cases", 15,
            "execution_time", "2024-01-01 10:00:00",
            "status", "completed",
            "execution_details", List.of(
                Map.of(
                    "case_id", 1,
                    "case_name", "用户登录测试",
                    "status", "passed",
                    "execution_time", "2024-01-01 10:01:00",
                    "response_time", "150ms"
                ),
                Map.of(
                    "case_id", 2,
                    "case_name", "用户注册测试",
                    "status", "failed",
                    "execution_time", "2024-01-01 10:02:00",
                    "error_message", "参数验证失败"
                )
            )
        );
        return Result.success("查询成功", reportDetail);
    }
    
    @GetMapping("/generate_report")
    public Result<Map<String, Object>> generateReport(
            @RequestParam(required = false) Long projectId,
            @RequestParam(required = false) Long testSuiteId
    ) {
        Map<String, Object> reportData = Map.of(
            "report_id", 12345,
            "project_id", projectId,
            "test_suite_id", testSuiteId,
            "status", "generating",
            "message", "报告生成中，请稍后查看"
        );
        return Result.success("报告生成请求已提交", reportData);
    }
    
    @GetMapping("/download_report")
    public Result<Map<String, Object>> downloadReport(
            @RequestParam Long id,
            @RequestParam(defaultValue = "json") String format
    ) {
        String downloadUrl = String.format("/api/ApiReportViewer/download/%d?format=%s", id, format);
        Map<String, Object> reportData = Map.of(
            "report_id", id,
            "download_url", downloadUrl,
            "format", format,
            "expires", "2024-01-15 23:59:59"
        );
        return Result.success("报告下载链接已生成", reportData);
    }
}
