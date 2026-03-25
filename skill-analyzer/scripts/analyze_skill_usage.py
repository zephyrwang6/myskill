#!/usr/bin/env python3
"""
分析 Skill 使用日志，输出频率排行和满意度统计
用法: python analyze_skill_usage.py [--days 7]
"""

import json
import os
import argparse
from datetime import datetime, timedelta
from collections import defaultdict

VAULT = os.environ.get('OBSIDIAN_VAULT', os.path.expanduser('~/Documents/obsidian'))
LOG_FILE = os.path.join(VAULT, '06 计划', 'skill_usage_log.jsonl')


def load_logs(days=7):
    if not os.path.exists(LOG_FILE):
        print(f"日志文件不存在：{LOG_FILE}")
        print("请先用 skill-logger 记录几次使用。")
        return []

    cutoff = datetime.now() - timedelta(days=days)
    records = []

    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get('_schema'):  # 跳过 schema 行
                continue
            record_date = datetime.strptime(data['date'], '%Y-%m-%d')
            if record_date >= cutoff:
                records.append(data)

    return records


def analyze(records, days):
    if not records:
        print(f"最近 {days} 天没有使用记录。")
        return

    # 统计
    skill_count = defaultdict(int)
    skill_satisfaction = defaultdict(list)
    skill_notes = defaultdict(list)

    for r in records:
        skill = r['skill']
        skill_count[skill] += 1
        skill_satisfaction[skill].append(r['satisfaction'])
        if r.get('note'):
            skill_notes[skill].append(r['note'])

    total_uses = len(records)
    unique_skills = len(skill_count)
    all_scores = [r['satisfaction'] for r in records]
    avg_overall = sum(all_scores) / len(all_scores)

    print(f"\n{'='*50}")
    print(f"📊 Skill 使用分析（最近 {days} 天）")
    print(f"{'='*50}")
    print(f"\n总览")
    print(f"  共使用 {total_uses} 次，覆盖 {unique_skills} 个不同 Skill")
    print(f"  整体平均满意度：{avg_overall:.1f} / 5")

    # 频率排行
    print(f"\n使用频率排行")
    print(f"  {'排名':<4} {'Skill':<25} {'次数':<6} {'平均满意度'}")
    print(f"  {'-'*50}")
    sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)
    for i, (skill, count) in enumerate(sorted_skills, 1):
        avg = sum(skill_satisfaction[skill]) / len(skill_satisfaction[skill])
        print(f"  {i:<4} {skill:<25} {count:<6} {avg:.1f}")

    # 低满意度 Skill
    low_satisfaction = [
        (skill, sum(scores) / len(scores), skill_notes[skill])
        for skill, scores in skill_satisfaction.items()
        if sum(scores) / len(scores) < 3.5
    ]
    if low_satisfaction:
        print(f"\n⚠️  满意度偏低的 Skill（< 3.5 分）")
        for skill, avg, notes in sorted(low_satisfaction, key=lambda x: x[1]):
            print(f"  {skill}：{avg:.1f} 分")
            if notes:
                print(f"    常见备注：{notes[-1]}")

    # 高频 Skill 建议自动化
    high_freq = [(s, c) for s, c in sorted_skills if c >= 5]
    if high_freq:
        print(f"\n💡 高频 Skill（≥5次），考虑自动化")
        for skill, count in high_freq:
            print(f"  {skill}（{count} 次）")

    print(f"\n{'='*50}")
    print(f"数据来源：{LOG_FILE}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description='分析 Skill 使用日志')
    parser.add_argument('--days', type=int, default=7, help='分析最近 N 天（默认 7）')
    args = parser.parse_args()

    records = load_logs(args.days)
    analyze(records, args.days)


if __name__ == '__main__':
    main()
