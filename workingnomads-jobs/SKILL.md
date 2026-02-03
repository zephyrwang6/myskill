# Working Nomads 远程工作爬取工具

从 workingnomads.com 爬取远程工作职位列表。

## 使用场景

- 获取最新的远程工作机会
- 按类别筛选技术、设计、产品等职位
- 定期抓取新职位并保存
- 支持前端开发等特定方向筛选

## 使用方法

当用户要求获取 workingnomads.com 的职位列表时触发：
- "爬取 workingnomads"
- "获取远程工作"
- "workingnomads jobs"
- "爬取前端职位"

## 触发词

- `workingnomads`
- `远程工作`
- `爬取工作`
- `获取职位列表`
- `前端职位`

## 功能特性

1. **基础爬取**: 获取网站所有职位
2. **关键词筛选**: 支持按技术栈筛选（前端、React、Vue 等）
3. **数据解析**: 自动提取公司、薪资、技能要求等信息
4. **多格式输出**: JSON、Markdown、飞书表格格式
5. **飞书集成**: 可直接保存到飞书知识库或多维表格

## 使用示例

```bash
# 爬取所有职位（默认50个）
cd skills/workingnomads-jobs
node scripts/scrape-workingnomads.js

# 只获取前端相关职位
node scripts/scrape-workingnomads.js --frontend --limit=30

# 按类别筛选
node scripts/scrape-workingnomads.js --category=engineering --limit=20

# 保存到飞书多维表格
python scripts/save_to_bitable.py -a APP_TOKEN -t tblXXX -f output/jobs.json
```

## 输出文件

- `output/workingnomads/jobs-YYYY-MM-DD.json` - 原始数据
- `output/workingnomads/jobs-YYYY-MM-DD.md` - Markdown 表格
- `output/workingnomads/jobs-feishu-YYYY-MM-DD.txt` - 飞书格式

## 配置

爬虫使用 Playwright 进行页面渲染，支持动态加载的 Angular 应用。
