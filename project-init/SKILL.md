---
name: project-init
description: 项目初始化引导，从需求拆解到目录结构搭建、技术选型和开发规范建立。
---

# 项目初始化

引导用户从零开始搭建项目，完成从需求梳理到可运行项目的全过程。

## 工作流程

### 1. 需求对齐

通过提问了解项目全貌：
- 产品类型：Web 应用、移动端、CLI 工具、桌面应用等
- 核心功能：列出 MVP 必须实现的功能
- 技术偏好：框架、语言、数据库等
- 目标平台：浏览器、iOS/Android、桌面等
- 部署方式：云服务、自托管、Serverless 等

### 2. 技术选型

根据需求推荐技术栈，说明选择理由：
- 前端框架（React/Vue/Svelte 等）
- 后端框架（Express/Fastify/Django 等）
- 数据库（PostgreSQL/SQLite/MongoDB 等）
- 构建工具（Vite/Webpack/Turbopack 等）
- 包管理器（npm/pnpm/bun 等）

### 3. 项目脚手架

执行项目初始化：
- 使用官方脚手架命令（如 `create-vite`、`create-next-app`）
- 配置 TypeScript、ESLint、Prettier
- 建立目录结构和模块划分
- 初始化 Git 仓库和 `.gitignore`

### 4. 开发规范

建立项目开发规范：
- 创建 `CLAUDE.md` 定义项目指引
- 配置代码风格（EditorConfig、Prettier）
- 建立提交规范（Conventional Commits）
- 编写基础 README 说明

### 5. 验证可运行

确保项目可以正常启动：
- 运行 `npm install` 安装依赖
- 运行开发服务器验证启动
- 运行 TypeScript 类型检查
- 确认基础测试框架可用

## 输出清单

完成初始化后，确认以下产出：
- [ ] 项目可正常 `npm run dev` 启动
- [ ] TypeScript 编译无报错
- [ ] ESLint/Prettier 配置就绪
- [ ] Git 仓库已初始化
- [ ] CLAUDE.md 项目指引已创建
- [ ] README.md 基础说明已编写
