#!/usr/bin/env node
/**
 * Session Start Hook
 * 会话开始时触发，显示项目信息
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function getGitInfo() {
  try {
    const branch = execSync('git branch --show-current', { encoding: 'utf8' }).trim();
    const status = execSync('git status --porcelain', { encoding: 'utf8' });
    const changedFiles = status.split('\n').filter(Boolean).length;
    return { branch, changedFiles };
  } catch {
    return { branch: 'unknown', changedFiles: 0 };
  }
}

function main() {
  const gitInfo = getGitInfo();
  
  const welcomeMessage = `
╔══════════════════════════════════════════════════════════════════╗
║                    🚀 AI Agent Testing Platform                   ║
╠══════════════════════════════════════════════════════════════════╣
║  🌿 分支: ${gitInfo.branch.padEnd(20)}  📝 变更: ${String(gitInfo.changedFiles).padEnd(10)}║
╠══════════════════════════════════════════════════════════════════╣
║  🛠️ 技术栈                                                        ║
║  后端: FastAPI + SQLModel + MySQL + MinIO + LangGraph            ║
║  前端: Vue 3 + Element Plus + Vuex + TailwindCSS                 ║
╠══════════════════════════════════════════════════════════════════╣
║  📋 可用技能: 23个 (后端5/前端2/移动端4/业务4/质量4/工程5)         ║
╚══════════════════════════════════════════════════════════════════╝
`;

  console.log(welcomeMessage);
  process.exit(0);
}

main();
