#!/usr/bin/env python3
"""
更新记忆系统文件的工具脚本
"""

import sys
from datetime import datetime

def get_current_month_file():
    """获取当前月份的L1文件路径"""
    now = datetime.now()
    return f"AI_MEMORY/L1_情境层/{now.year}-{now.month:02d}.md"

def format_l1_entry(date, event_type, content, emotion=None, tags=None):
    """格式化L1情境层记录"""
    entry = f"\n### {date}\n\n"
    entry += f"#### {event_type}\n"
    entry += f"- **内容**：{content}\n"
    if emotion:
        entry += f"- **情绪**：{emotion}\n"
    if tags:
        tag_str = " ".join([f"#{tag}" for tag in tags])
        entry += f"- **标签**：`{tag_str}`\n"
    return entry

def check_pattern_occurrence(keyword, memory_path="AI_MEMORY/L1_情境层/"):
    """检查关键词在历史记录中的出现次数"""
    # 这里应该使用Grep工具，而不是实际执行
    # 返回提示使用Grep
    return f"Use Grep to search '{keyword}' in {memory_path}"

if __name__ == "__main__":
    # 测试获取当前月份文件
    print(f"Current month file: {get_current_month_file()}")

    # 测试格式化L1条目
    entry = format_l1_entry(
        date="2025-12-27",
        event_type="重要决策",
        content="决定采用Claude Code方案搭建AI记忆系统",
        emotion="期待",
        tags=["决策", "AI", "系统"]
    )
    print("Formatted L1 entry:")
    print(entry)
