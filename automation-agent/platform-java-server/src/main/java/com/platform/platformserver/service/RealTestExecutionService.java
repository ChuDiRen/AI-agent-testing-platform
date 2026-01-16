package com.platform.platformserver.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.platform.platformserver.common.Result;
import com.platform.platformserver.entity.ApiInfoCase;
import com.platform.platformserver.entity.ApiInfoCaseStep;
import com.platform.platformserver.entity.ApiKeyWord;
import com.platform.platformserver.entity.ApiOperationType;
import com.platform.platformserver.mapper.ApiInfoCaseMapper;
import com.platform.platformserver.mapper.ApiInfoCaseStepMapper;
import com.platform.platformserver.mapper.ApiKeyWordMapper;
import com.platform.platformserver.mapper.ApiOperationTypeMapper;
import com.platform.platformserver.utils.SafeCommandExecutor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 真实的测试执行服务
 * 对应Flask版本的CLI执行功能
 */
@Slf4j
@Service
public class RealTestExecutionService {

    @Autowired
    private ApiInfoCaseMapper apiInfoCaseMapper;

    @Autowired
    private ApiInfoCaseStepMapper apiInfoCaseStepMapper;

    @Autowired
    private ApiKeyWordMapper apiKeyWordMapper;

    @Autowired
    private ApiOperationTypeMapper apiOperationTypeMapper;

    @Autowired
    private SafeCommandExecutor commandExecutor;

    @Autowired
    private ObjectMapper objectMapper;

    @Value("${test.execution.temp-dir:/tmp/test-execution}")
    private String tempDir;

    @Value("${test.execution.keywords-dir:/tmp/keywords}")
    private String keywordsDir;

    @Value("${test.execution.report-dir:/tmp/reports}")
    private String reportDir;

    private static final DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm-ss");

    /**
     * 执行测试用例（对应Flask的debugTest功能）
     */
    public Result<Map<String, Object>> executeTestCase(Long caseId) {
        try {
            // 1. 获取测试用例信息
            ApiInfoCase testCase = apiInfoCaseMapper.selectById(caseId);
            if (testCase == null) {
                return Result.error("测试用例不存在");
            }

            // 2. 生成执行UUID
            String executeUuid = UUID.randomUUID().toString();
            String timestamp = LocalDateTime.now().format(formatter);

            // 3. 准备执行环境
            String runTmpDir = prepareExecutionDirectory(executeUuid, timestamp);
            
            // 4. 生成测试用例文件
            String testCaseFile = generateTestCaseFile(testCase, runTmpDir);
            
            // 5. 执行测试命令
            Map<String, Object> executionResult = executeTestCommand(runTmpDir, testCaseFile);
            
            // 6. 生成测试报告
            String reportPath = generateTestReport(runTmpDir, executeUuid);
            
            // 7. 构建返回结果
            Map<String, Object> result = new HashMap<>();
            result.put("execute_uuid", executeUuid);
            result.put("status", "completed");
            result.put("message", "测试用例执行完成");
            result.put("report_path", "/report/" + executeUuid + "/");
            result.put("case_name", testCase.getCaseName());
            result.put("execution_result", executionResult);
            result.put("report_html_path", reportPath + "/index.html");
            
            log.info("测试用例执行完成: caseId={}, executeUuid={}", caseId, executeUuid);
            
            return Result.success("测试用例执行成功", result);

        } catch (Exception e) {
            log.error("测试用例执行失败: caseId={}", caseId, e);
            return Result.error("测试用例执行失败: " + e.getMessage());
        }
    }

    /**
     * 批量执行测试用例
     */
    public Result<Map<String, Object>> executeBatchTest(List<Long> caseIds) {
        try {
            String executeUuid = UUID.randomUUID().toString();
            String timestamp = LocalDateTime.now().format(formatter);
            
            // 准备批量执行环境
            String batchDir = prepareBatchExecutionDirectory(executeUuid, timestamp);
            
            // 生成所有测试用例文件
            List<String> testCaseFiles = new ArrayList<>();
            for (Long caseId : caseIds) {
                ApiInfoCase testCase = apiInfoCaseMapper.selectById(caseId);
                if (testCase != null) {
                    String caseFile = generateTestCaseFile(testCase, batchDir);
                    testCaseFiles.add(caseFile);
                }
            }
            
            // 执行批量测试
            Map<String, Object> batchResult = executeBatchTestCommand(batchDir, testCaseFiles);
            
            // 生成批量报告
            String reportPath = generateTestReport(batchDir, executeUuid);
            
            // 构建返回结果
            Map<String, Object> result = new HashMap<>();
            result.put("execute_uuid", executeUuid);
            result.put("status", "completed");
            result.put("total_cases", caseIds.size());
            result.put("report_path", "/report/" + executeUuid + "/");
            result.put("batch_result", batchResult);
            result.put("report_html_path", reportPath + "/index.html");
            
            return Result.success("批量测试执行成功", result);

        } catch (Exception e) {
            log.error("批量测试执行失败", e);
            return Result.error("批量测试执行失败: " + e.getMessage());
        }
    }

    /**
     * 准备执行目录
     */
    private String prepareExecutionDirectory(String executeUuid, String timestamp) throws IOException {
        String runDir = Paths.get(tempDir, executeUuid + "_" + timestamp).toString();
        Files.createDirectories(Paths.get(runDir));
        return runDir;
    }

    /**
     * 准备批量执行目录
     */
    private String prepareBatchExecutionDirectory(String executeUuid, String timestamp) throws IOException {
        String batchDir = Paths.get(tempDir, "batch_" + executeUuid + "_" + timestamp).toString();
        Files.createDirectories(Paths.get(batchDir));
        return batchDir;
    }

    /**
     * 生成测试用例YAML文件
     */
    private String generateTestCaseFile(ApiInfoCase testCase, String runDir) throws IOException {
        // 获取测试步骤
        List<ApiInfoCaseStep> steps = apiInfoCaseStepMapper.selectList(
            new com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<ApiInfoCaseStep>()
                .eq("api_case_info_id", testCase.getId())
                .orderByAsc("run_order")
        );

        // 构建测试用例数据
        Map<String, Object> testCaseData = new HashMap<>();
        testCaseData.put("test_name", testCase.getCaseName());
        testCaseData.put("test_description", testCase.getCaseDesc());
        
        List<Map<String, Object>> testSteps = new ArrayList<>();
        for (ApiInfoCaseStep step : steps) {
            Map<String, Object> stepData = new HashMap<>();
            stepData.put("step_name", step.getStepDesc());
            stepData.put("run_order", step.getRunOrder());
            
            // 获取关键字信息
            ApiKeyWord keyword = apiKeyWordMapper.selectById(step.getKeyWordId());
            if (keyword != null) {
                ApiOperationType operationType = apiOperationTypeMapper.selectById(keyword.getOperationTypeId());
                
                stepData.put("keyword", keyword.getKeywordFunName());
                stepData.put("keyword_desc", keyword.getKeywordDesc());
                if (operationType != null) {
                    stepData.put("operation_type", operationType.getOperationTypeName());
                }
            }
            
            // 解析变量
            if (step.getRefVariable() != null && !step.getRefVariable().isEmpty()) {
                try {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> variables = (Map<String, Object>) objectMapper.readValue(step.getRefVariable(), Map.class);
                    stepData.put("variables", variables);
                } catch (Exception e) {
                    stepData.put("variables", new HashMap<>());
                }
            }
            
            testSteps.add(stepData);
        }
        
        testCaseData.put("test_steps", testSteps);

        // 写入YAML文件
        String fileName = testCase.getCaseName().replaceAll("[^a-zA-Z0-9]", "_") + ".yaml";
        String filePath = Paths.get(runDir, fileName).toString();
        
        try (FileWriter writer = new FileWriter(filePath)) {
            // 简单的YAML格式输出
            writer.write(convertToYaml(testCaseData));
        }

        return filePath;
    }

    /**
     * 执行测试命令
     */
    private Map<String, Object> executeTestCommand(String runDir, String testCaseFile) 
            throws SafeCommandExecutor.CommandExecutionException {
        
        // 构建安全的命令
        List<String> command = Arrays.asList(
            "huace-apirun",
            "--cases=" + runDir,
            "--keyDir=" + keywordsDir,
            "-sv",
            "--capture=tee-sys"
        );

        // 执行命令
        SafeCommandExecutor.ExecutionResult result = commandExecutor.executeCommand(command, runDir);
        
        // 解析执行结果
        Map<String, Object> executionResult = new HashMap<>();
        executionResult.put("command", String.join(" ", command));
        executionResult.put("output", result.getOutput());
        executionResult.put("exit_code", result.getExitCode());
        executionResult.put("execution_time", System.currentTimeMillis());
        
        return executionResult;
    }

    /**
     * 执行批量测试命令
     */
    private Map<String, Object> executeBatchTestCommand(String batchDir, List<String> testCaseFiles) 
            throws SafeCommandExecutor.CommandExecutionException {
        
        // 构建批量测试命令
        List<String> command = Arrays.asList(
            "huace-apirun",
            "--cases=" + batchDir,
            "--keyDir=" + keywordsDir,
            "-sv",
            "--capture=tee-sys",
            "--alluredir=" + Paths.get(batchDir, "allure-data")
        );

        // 执行命令
        SafeCommandExecutor.ExecutionResult result = commandExecutor.executeCommand(command, batchDir);
        
        // 解析批量执行结果
        Map<String, Object> batchResult = new HashMap<>();
        batchResult.put("command", String.join(" ", command));
        batchResult.put("output", result.getOutput());
        batchResult.put("exit_code", result.getExitCode());
        batchResult.put("test_cases_count", testCaseFiles.size());
        batchResult.put("execution_time", System.currentTimeMillis());
        
        return batchResult;
    }

    /**
     * 生成测试报告
     */
    private String generateTestReport(String runDir, String executeUuid) 
            throws SafeCommandExecutor.CommandExecutionException, IOException {
        
        String reportDataDir = Paths.get(runDir, "allure-data").toString();
        String reportHtmlDir = Paths.get(reportDir, executeUuid).toString();
        
        // 确保报告数据目录存在
        Files.createDirectories(Paths.get(reportDataDir));
        Files.createDirectories(Paths.get(reportHtmlDir));
        
        // 生成Allure报告
        List<String> command = Arrays.asList(
            "allure",
            "generate",
            reportDataDir,
            "-c",
            "-o",
            reportHtmlDir
        );

        try {
            commandExecutor.executeCommand(command, reportDir);
            log.info("测试报告生成成功: {}", reportHtmlDir);
        } catch (SafeCommandExecutor.CommandExecutionException e) {
            log.warn("测试报告生成失败，但测试执行已完成: {}", e.getMessage());
            // 即使报告生成失败，也返回路径
        }

        return reportHtmlDir;
    }

    /**
     * 简单的YAML转换（实际项目中建议使用SnakeYAML库）
     */
    private String convertToYaml(Map<String, Object> data) {
        StringBuilder yaml = new StringBuilder();
        yaml.append("test_name: ").append(data.get("test_name")).append("\n");
        yaml.append("test_description: ").append(data.get("test_description")).append("\n");
        yaml.append("test_steps:\n");
        
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> steps = (List<Map<String, Object>>) data.get("test_steps");
        for (Map<String, Object> step : steps) {
            yaml.append("  - step_name: ").append(step.get("step_name")).append("\n");
            yaml.append("    run_order: ").append(step.get("run_order")).append("\n");
            yaml.append("    keyword: ").append(step.get("keyword")).append("\n");
            if (step.containsKey("variables")) {
                yaml.append("    variables: ").append(step.get("variables")).append("\n");
            }
        }
        
        return yaml.toString();
    }

    /**
     * 检查执行环境
     */
    public Result<Map<String, Object>> checkExecutionEnvironment() {
        try {
            SafeCommandExecutor.EnvironmentCheckResult checkResult = commandExecutor.checkEnvironment();
            
            Map<String, Object> result = new HashMap<>();
            result.put("ready", checkResult.isReady());
            result.put("available_commands", checkResult.getAvailableCommands());
            result.put("missing_commands", checkResult.getMissingCommands());
            result.put("execution_enabled", commandExecutor.getAllowedCommands());
            
            if (checkResult.isReady()) {
                return Result.success("执行环境检查通过", result);
            } else {
                return Result.error("执行环境检查失败");
            }
            
        } catch (Exception e) {
            return Result.error("执行环境检查异常: " + e.getMessage());
        }
    }
}
