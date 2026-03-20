---
name: meridian
description: Meridian 项目集成助手。当用户提到 Meridian、导航面板、看板配置、分析模块时触发。帮助用户通过 Claude Code 为 Meridian 仪表盘生成左侧导航、自定义面板和可视化模块。
---

# Meridian — Obsidian AI 驾驶舱集成技能

## ⚠️ 核心规则

> **一次只创建一个面板。** 用户的每条指令只请求创建一个导航面板。绝对不要一次性为所有文件夹批量生成导航。每次只创建一个组件 + 注册到 page.tsx。

## 什么是 Meridian

Meridian 是一个基于 Next.js 的本地 Web 应用，作为 Obsidian 知识库的可视化驾驶舱。

### 安装与初始化（克隆项目）
如果用户的 Obsidian Vault 中还没有 Meridian 项目代码（即找不到 `05 工具箱/vault-pilot/` 目录），你需要从 GitHub 获取官方代码为你完成初次安装部署：

```bash
# 进入工具箱目录拉取代码
cd "05 工具箱"
git clone https://github.com/zephyrwang6/VaultPilot.git vault-pilot
cd vault-pilot
npm install
```

**项目位置**：`05 工具箱/vault-pilot/`（目录名为 vault-pilot，产品名为 Meridian）
**启动方式**：`cd "05 工具箱/vault-pilot" && npm run dev -- --port 3001`
**访问地址**：http://localhost:3001

## 项目结构

```
vault-pilot/
├── app/
│   ├── page.tsx                    # 主页面（侧边栏 + 内容区）
│   ├── layout.tsx                  # 布局 + Inter 字体
│   ├── globals.css                 # 暗/浅双主题 + 玻璃态
│   ├── components/
│   │   ├── AgentPanel.tsx          # Agent 面板（CLI + .claude.md + Skills）
│   │   ├── FoldersPanel.tsx        # 文件夹面板（文件夹树 + 快捷指令）
│   │   ├── FolderAnalysisModal.tsx # 文件夹分析弹窗（4种视图）
│   │   ├── UsagePanel.tsx          # Claude Code 用量统计
│   │   ├── DynamicPanel.tsx        # 动态面板渲染器
│   │   └── Onboarding.tsx          # 首次引导绑定
│   └── api/
│       ├── config/route.ts         # 配置读写 + .claude.md
│       ├── vault/route.ts          # 文件夹结构扫描
│       ├── skills/route.ts         # Skills 库扫描
│       ├── claude/route.ts         # 打开终端执行
│       ├── pick-folder/route.ts    # 原生文件夹选择器
│       ├── folder-analysis/route.ts # 文件夹深度分析
│       └── usage/route.ts          # Claude Code 用量数据
└── lib/types.ts                    # 核心类型定义
```

## 设计参考

面板设计参考 `05 工具箱/obsidian-dashboard/my-app/app/components/desktop/` 下的组件：

| 面板 | 参考文件 | 功能 |
|------|----------|------|
| 总览 | `OverviewPanel.tsx` | 数据概况、最近文档、日程、任务 |
| 创作 | `ContentPanel.tsx` | 独立文章列表、专栏章节列表 |
| 计划 | `GoalsPanel.tsx` | 年度目标、周计划进度 |
| 复盘 | `ReviewPanel.tsx` | 本周产出统计进度条、完成任务 |

**注意：** 参考的是设计风格和功能布局。Meridian 使用自己的 CSS 类（glass-card 等），不用 shadcn/ui。**数据必须从本地文件系统动态读取，不要硬编码。**

## CSS 设计规范

| 类名 | 用途 |
|------|------|
| `glass-card` | 玻璃态卡片容器 |
| `rounded-2xl p-5` | 标准卡片内边距 |
| `stat-value` | 大号数字 |
| `text-violet-400` | 主色调图标 |
| `text-muted-foreground` | 次要文字 |
| `bg-secondary/30` | 悬停/背景 |
| `stagger-children` | 子元素交错动画 |
| `gradient-text` | 渐变文字 |

## 可用 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/config` | GET | 读取配置 + .claude.md |
| `/api/vault` | GET | 扫描 Vault 文件夹结构 |
| `/api/folder-analysis?path=...` | GET | 深度分析指定文件夹 |
| `/api/skills` | GET | 读取 Skills 列表 |
| `/api/usage` | GET | Claude Code 用量统计 |

## 创建面板工作流程

每次创建一个面板，按以下步骤：

### 第 1 步：读取参考

```bash
# 读取 obsidian-dashboard 对应面板的设计
cat "05 工具箱/obsidian-dashboard/my-app/app/components/desktop/OverviewPanel.tsx"
```

### 第 2 步：创建组件

在 `05 工具箱/vault-pilot/app/components/` 下创建 `XxxPanel.tsx`：
- 数据通过 API（`/api/folder-analysis`）或读文件获取
- 必须使用 glass-card、stat-value 等 Meridian CSS 类
- 不要用 shadcn/ui 组件

**组件模板**：

```tsx
'use client';

import { useState, useEffect } from 'react';
import { Loader2, SomeIcon } from 'lucide-react';

interface PanelProps {
  vaultPath: string;
}

export function XxxPanel({ vaultPath }: PanelProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/folder-analysis?path=${encodeURIComponent(vaultPath + '/目标文件夹')}`)
      .then(r => r.json())
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [vaultPath]);

  if (loading) return <div className="flex justify-center py-16"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>;

  return (
    <div className="space-y-5 stagger-children">
      <div className="grid grid-cols-3 gap-3">
        <div className="glass-card rounded-xl p-4">
          <div className="stat-value text-2xl">数值</div>
          <div className="text-[10px] text-muted-foreground">标签</div>
        </div>
      </div>
      <div className="glass-card rounded-2xl p-5">
        <div className="text-sm font-medium mb-3">标题</div>
        <div className="space-y-1.5">{/* 列表项 */}</div>
      </div>
    </div>
  );
}
```

### 第 3 步：注册到 page.tsx

修改 `05 工具箱/vault-pilot/app/page.tsx`，需要改 3 处：

```tsx
// 1. 导入（在文件顶部 import 区域）
import { XxxPanel } from './components/XxxPanel';

// 2. 在 defaultNavItems 数组添加（约第 22 行）
{ id: 'xxx', label: '面板名', icon: SomeIcon },

// 3. 在 renderPanel() 的 switch 中添加 case（约第 107 行）
case 'xxx':
  return <XxxPanel vaultPath={config.vaultPath} />;
```

### 第 4 步：告知用户

完成后告知用户：已创建「XXX」面板，请刷新 http://localhost:3001 查看。
