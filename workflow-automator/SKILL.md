---
name: workflow-automator
description: 自动化工作流编排，支持 CI/CD 配置、脚本生成、定时任务和 Git Hooks 设置。
---

# 自动化工作流

帮助用户设计和实现项目中的自动化工作流，减少重复性手动操作。

## 能力范围

1. **CI/CD 流水线** — GitHub Actions、GitLab CI 等配置文件生成和优化
2. **构建脚本** — Makefile、npm scripts、shell 脚本编写
3. **Git Hooks** — pre-commit、commit-msg 等钩子配置（husky、lint-staged）
4. **定时任务** — cron 表达式、scheduled tasks 配置
5. **代码质量自动化** — ESLint、Prettier、TypeScript 检查的自动化集成
6. **发布流程** — 版本管理、changelog 生成、自动发布脚本

## 工作流程

### 1. 了解项目现状

- 询问项目技术栈、代码托管平台、现有的自动化配置
- 读取 `package.json`、`.github/workflows/`、`Makefile` 等文件了解现状

### 2. 识别自动化机会

根据项目情况推荐可自动化的环节：
- 代码提交时自动检查（lint、format、type-check）
- PR 合并时自动测试和构建
- 版本发布时自动打包和部署
- 重复性操作的脚本封装

### 3. 实现自动化配置

- 生成配置文件，确保语法正确
- 提供必要的环境变量和密钥配置说明
- 编写清晰的注释说明每个步骤的作用

### 4. 验证和测试

- 检查配置文件语法
- 提供本地测试命令（如 `act` 测试 GitHub Actions）
- 列出验证清单确保配置正确

## 注意事项

- 优先使用项目已有的工具和配置，避免引入不必要的依赖
- 配置文件中的敏感信息（密钥、token）必须使用环境变量或 secrets
- 为每个自动化步骤添加清晰的注释
- 考虑失败情况的处理和通知机制
