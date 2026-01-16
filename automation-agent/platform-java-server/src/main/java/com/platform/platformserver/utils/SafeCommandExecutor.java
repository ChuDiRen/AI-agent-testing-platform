package com.platform.platformserver.utils;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;

/**
 * 安全的CLI命令执行工具类
 * 提供安全的命令执行环境，防止命令注入攻击
 */
@Slf4j
@Component
public class SafeCommandExecutor {

    @Value("${test.execution.enabled:false}")
    private boolean executionEnabled;

    @Value("${test.execution.timeout:300}")
    private int executionTimeout;

    @Value("${test.execution.allowed-commands:huace-apirun,allure}")
    private String allowedCommands;

    @Value("${test.execution.base-dir:/tmp}")
    private String baseDir;

    // 危险字符模式
    private static final Pattern DANGEROUS_CHARS = Pattern.compile(".*[;&|`$(){}\\[\\]<>].*");
    
    // 路径遍历模式
    private static final Pattern PATH_TRAVERSAL = Pattern.compile(".*\\.\\..*");

    /**
     * 安全执行命令
     */
    public ExecutionResult executeCommand(List<String> command, String workingDir) 
            throws CommandExecutionException {
        
        if (!executionEnabled) {
            throw new CommandExecutionException("CLI执行功能未启用");
        }

        // 安全检查
        validateCommand(command);
        validateWorkingDirectory(workingDir);

        try {
            log.info("执行命令: {}", String.join(" ", command));
            log.info("工作目录: {}", workingDir);

            ProcessBuilder pb = new ProcessBuilder(command);
            pb.directory(new File(workingDir));
            pb.redirectErrorStream(true);

            Process process = pb.start();

            // 读取输出
            String output = readProcessOutput(process);
            
            // 等待执行完成
            boolean finished = process.waitFor(executionTimeout, TimeUnit.SECONDS);
            
            if (!finished) {
                process.destroyForcibly();
                throw new CommandExecutionException("命令执行超时");
            }

            int exitCode = process.exitValue();
            log.info("命令执行完成，退出码: {}", exitCode);

            if (exitCode != 0) {
                throw new CommandExecutionException(
                    String.format("命令执行失败，退出码: %d, 输出: %s", exitCode, output)
                );
            }

            return new ExecutionResult(exitCode, output);

        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new CommandExecutionException("命令执行被中断", e);
        } catch (IOException e) {
            throw new CommandExecutionException("命令执行IO异常", e);
        }
    }

    /**
     * 验证命令安全性
     */
    private void validateCommand(List<String> command) throws CommandExecutionException {
        if (command == null || command.isEmpty()) {
            throw new CommandExecutionException("命令不能为空");
        }

        String mainCommand = command.get(0);
        
        // 检查命令是否在允许列表中
        List<String> allowedList = Arrays.asList(allowedCommands.split(","));
        if (!allowedList.contains(mainCommand)) {
            throw new CommandExecutionException(
                String.format("命令 '%s' 不在允许列表中: %s", mainCommand, allowedCommands)
            );
        }

        // 检查参数中的危险字符
        for (String arg : command) {
            if (DANGEROUS_CHARS.matcher(arg).matches()) {
                throw new CommandExecutionException(
                    String.format("参数包含危险字符: %s", arg)
                );
            }
        }
    }

    /**
     * 验证工作目录安全性
     */
    private void validateWorkingDirectory(String workingDir) throws CommandExecutionException {
        if (workingDir == null || workingDir.trim().isEmpty()) {
            throw new CommandExecutionException("工作目录不能为空");
        }

        // 检查路径遍历攻击
        if (PATH_TRAVERSAL.matcher(workingDir).matches()) {
            throw new CommandExecutionException(
                String.format("工作目录包含路径遍历字符: %s", workingDir)
            );
        }

        // 确保路径在基础目录内
        Path normalizedPath = Paths.get(workingDir).normalize();
        Path basePath = Paths.get(baseDir).normalize();
        
        if (!normalizedPath.startsWith(basePath)) {
            throw new CommandExecutionException(
                String.format("工作目录不在允许的基础目录内: %s", workingDir)
            );
        }

        // 检查目录是否存在
        if (!Files.exists(normalizedPath)) {
            throw new CommandExecutionException(
                String.format("工作目录不存在: %s", workingDir)
            );
        }
    }

    /**
     * 读取进程输出
     */
    private String readProcessOutput(Process process) throws IOException {
        StringBuilder output = new StringBuilder();
        try (InputStream inputStream = process.getInputStream();
             BufferedReader reader = new BufferedReader(
                 new InputStreamReader(inputStream, StandardCharsets.UTF_8))) {
            
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
        }
        return output.toString();
    }

    /**
     * 检查必需的命令是否可用
     */
    public boolean checkCommandAvailability(String command) {
        try {
            ProcessBuilder pb = new ProcessBuilder(command, "--version");
            Process process = pb.start();
            return process.waitFor(5, TimeUnit.SECONDS);
        } catch (Exception e) {
            log.warn("检查命令可用性失败: {}", command, e);
            return false;
        }
    }

    /**
     * 获取所有允许的命令
     */
    public List<String> getAllowedCommands() {
        return Arrays.asList(allowedCommands.split(","));
    }

    /**
     * 检查执行环境是否就绪
     */
    public EnvironmentCheckResult checkEnvironment() {
        List<String> missingCommands = new ArrayList<>();
        List<String> availableCommands = new ArrayList<>();

        for (String command : getAllowedCommands()) {
            if (checkCommandAvailability(command)) {
                availableCommands.add(command);
            } else {
                missingCommands.add(command);
            }
        }

        boolean ready = missingCommands.isEmpty();
        return new EnvironmentCheckResult(ready, availableCommands, missingCommands);
    }

    /**
     * 执行结果类
     */
    public static class ExecutionResult {
        private final int exitCode;
        private final String output;

        public ExecutionResult(int exitCode, String output) {
            this.exitCode = exitCode;
            this.output = output;
        }

        public int getExitCode() { return exitCode; }
        public String getOutput() { return output; }
    }

    /**
     * 环境检查结果类
     */
    public static class EnvironmentCheckResult {
        private final boolean ready;
        private final List<String> availableCommands;
        private final List<String> missingCommands;

        public EnvironmentCheckResult(boolean ready, List<String> availableCommands, List<String> missingCommands) {
            this.ready = ready;
            this.availableCommands = availableCommands;
            this.missingCommands = missingCommands;
        }

        public boolean isReady() { return ready; }
        public List<String> getAvailableCommands() { return availableCommands; }
        public List<String> getMissingCommands() { return missingCommands; }
    }

    /**
     * 命令执行异常
     */
    public static class CommandExecutionException extends Exception {
        public CommandExecutionException(String message) {
            super(message);
        }

        public CommandExecutionException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
