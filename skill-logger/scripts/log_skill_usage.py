#!/usr/bin/env python3
"""
记录一次 Skill 使用情况到日志文件
用法: python log_skill_usage.py --skill x-post --scene "..." --satisfaction 4 [--note "..."]
"""

import json
import os
import argparse
from datetime import datetime

# 日志文件路径，从环境变量读取 vault 路径
VAULT = os.environ.get('OBSIDIAN_VAULT', os.path.expanduser('~/Documents/obsidian'))
LOG_FILE = os.path.join(VAULT, '06 计划', 'skill_usage_log.jsonl')

WEEKDAY_MAP = {0: '周一', 1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日'}


def get_week_number(dt):
    return f"W{dt.isocalendar()[1]:02d}"


def append_log(skill, scene, satisfaction, note=''):
    now = datetime.now()
    record = {
        'date': now.strftime('%Y-%m-%d'),
        'weekday': WEEKDAY_MAP[now.weekday()],
        'week': get_week_number(now),
        'skill': skill,
        'scene': scene,
        'satisfaction': int(satisfaction),
        'note': note,
    }

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    # 如果文件不存在，先写入 schema 行
    if not os.path.exists(LOG_FILE):
        schema = {
            '_schema': 'skill_usage_log',
            '_version': '1.0',
            '_description': 'Skill 使用日志。每次使用 Skill 后追加一条记录，用于频率分析和满意度追踪。'
        }
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            f.write(json.dumps(schema, ensure_ascii=False) + '\n')

    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + '\n')

    return record


def main():
    parser = argparse.ArgumentParser(description='记录 Skill 使用日志')
    parser.add_argument('--skill', required=True, help='Skill 名称，如 x-post')
    parser.add_argument('--scene', required=True, help='使用场景描述')
    parser.add_argument('--satisfaction', required=True, type=int, choices=range(1, 6),
                        help='满意度 1-5')
    parser.add_argument('--note', default='', help='备注（可选）')
    args = parser.parse_args()

    record = append_log(args.skill, args.scene, args.satisfaction, args.note)

    print(f"✅ 已记录：{record['skill']}（满意度 {record['satisfaction']}/5）")
    print(f"   场景：{record['scene']}")
    if record['note']:
        print(f"   备注：{record['note']}")
    print(f"   写入：{LOG_FILE}")


if __name__ == '__main__':
    main()
