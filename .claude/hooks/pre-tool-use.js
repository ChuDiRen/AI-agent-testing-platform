#!/usr/bin/env node
/**
 * Pre Tool Use Hook
 * 工具执行前触发，进行安全检查
 * 从 stdin 读取 JSON 数据
 */

const dangerousPatterns = [
  /rm\s+-rf\s+[\/~]/,
  /rm\s+-rf\s+\*/,
  /rmdir\s+\/s\s+\/q/,
  /del\s+\/f\s+\/s\s+\/q/,
  /git\s+push\s+.*--force\s+.*main/,
  /git\s+push\s+.*--force\s+.*master/,
  /git\s+reset\s+--hard/,
  /chmod\s+777/
];

async function readStdin() {
  return new Promise((resolve) => {
    let data = '';
    const timeout = setTimeout(() => resolve(data), 100);
    
    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (chunk) => {
      clearTimeout(timeout);
      data += chunk;
    });
    process.stdin.on('end', () => {
      clearTimeout(timeout);
      resolve(data);
    });
    
    if (!process.stdin.isTTY) {
      process.stdin.resume();
    } else {
      clearTimeout(timeout);
      resolve('');
    }
  });
}

function checkDangerousCommand(cmd) {
  for (const pattern of dangerousPatterns) {
    if (pattern.test(cmd)) {
      return { isDangerous: true, pattern: pattern.toString() };
    }
  }
  return { isDangerous: false };
}

async function main() {
  try {
    const stdinData = await readStdin();
    let command = '';
    
    if (stdinData.trim()) {
      try {
        const inputData = JSON.parse(stdinData);
        command = inputData.tool_input?.command || '';
      } catch {
        command = stdinData;
      }
    }
    
    if (!command) {
      process.exit(0);
    }
    
    const result = checkDangerousCommand(command);
    
    if (result.isDangerous) {
      console.error(`⚠️ 安全警告: 检测到危险命令模式 ${result.pattern}`);
      process.exit(2); // 退出码 2 表示阻塞
    }
    
    process.exit(0);
  } catch {
    process.exit(0);
  }
}

main();
