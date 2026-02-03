# Working Nomads Scraper

从 Working Nomads 抓取远程职位信息，生成 Markdown 格式并可上传到飞书多维表格。

## 功能

- 从 Working Nomads API 抓取职位数据
- 支持 Development + Design 类别筛选
- 自动生成 Markdown 格式文档
- 支持上传到飞书多维表格
- 保留薪资、技能标签等完整信息

## 安装

```bash
cd ~/.claude/skills/workingnomads-scraper
pip install -r requirements.txt
```

## 使用

### 抓取职位

```bash
python3 -m scripts.main --category Development --size 50
```

参数说明：
- `--category`, `-c`: 职位类别 (Development, Design 等，默认: Development)
- `--size`, `-s`: 抓取数量 (默认: 50)
- `--output-dir`, `-o`: 输出目录 (默认: data)

### 上传到飞书

```bash
python3 scripts/add_records.py --file data/development_jobs_20260203_112246.json
```

## 输出文件

抓取的数据会生成两个文件：

1. **Markdown 文件** - `data/{category}_jobs_{timestamp}.md`
   - 包含统计概览
   - 完整的职位列表
   - 公司、地点、薪资、描述、申请链接

2. **JSON 文件** - `data/{category}_jobs_{timestamp}.json`
   - 结构化数据
   - 可用于程序处理

## 数据字段

| 字段 | 说明 |
|------|------|
| title | 职位名称 |
| company | 公司名称 |
| location | 工作地点 |
| position_type | 职位类型 (Full-time/Part-time/Freelance) |
| salary | 薪资信息 |
| experience | 经验级别 |
| tags | 技能标签 |
| description | 职位描述 |
| apply_url | 申请链接 |

## 典型职位

- Senior Software Engineer @ Reddit ($372,400/year)
- Product Designer @ Figma ($294,000/year)
- Staff ML Engineer @ Pinterest ($389,753/year)
- Senior ML Engineer @ Signifyd ($190,000/year)

## 配合飞书使用

1. 运行脚本生成 Markdown 和 JSON 文件
2. 使用 feishu-wiki skill 保存到飞书知识库
3. 或使用 `add_records.py` 直接上传到多维表格

```bash
# 查看飞书多维表格
python3 feishu-wiki/scripts/read_bitable.py --url "https://my.feishu.cn/wiki/xxx?table=xxx"

# 上传职位数据
python3 feishu-wiki/scripts/add_records.py --file data/jobs.json
```

## 依赖

- requests >= 2.31.0
- beautifulsoup4 >= 4.12.0

## License

MIT
