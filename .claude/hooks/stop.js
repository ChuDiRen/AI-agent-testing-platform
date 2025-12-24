#!/usr/bin/env node
/**
 * Stop Hook
 * AI 完成回答后触发
 */

const { execSync } = require('child_process');

function getCodeChanges() {
  try {
    const status = execSync('git status --porcelain', { encoding: 'utf8' });
    if (!status.trim()) {
      return { hasChanges: false, files: [] };
    }
    
    const files = status.split('\n')
      .filter(Boolean)
      .map(line => ({
        status: line.substring(0, 2).trim(),
        file: line.substring(3)
      }));
    
    return { hasChanges: true, files };
  } catch {
    return { hasChanges: false, files: [] };
  }
}

function main() {
  const changes = getCodeChanges();
  
  if (!changes.hasChanges) {
    process.exit(0);
  }
  
  const frontend = changes.files.filter(f => f.file.match(/\.(vue|tsx?|jsx?)$/)).length;
  const backend = changes.files.filter(f => f.file.match(/\.py$/)).length;
  
  if (frontend > 0 || backend > 0) {
    console.log(`✨ 变更: 前端 ${frontend} 文件, 后端 ${backend} 文件`);
  }
  
  process.exit(0);
}

main();
