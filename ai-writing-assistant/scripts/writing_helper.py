#!/usr/bin/env python3
"""
AI写作助手工具
提供常用的写作辅助功能
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class WritingHelper:
    def __init__(self):
        self.stop_words = {
            '中文': ['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'],
            '英文': ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'I', 'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at']
        }

    def analyze_text(self, text: str) -> Dict:
        """
        分析文本的基本信息
        """
        # 统计字数
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        total_words = len(text.replace(' ', ''))
        sentences = len(re.findall(r'[。！？.!?]+', text))
        paragraphs = len([p for p in text.split('\n') if p.strip()])

        # 估算阅读时间（按每分钟500字计算）
        reading_time = max(1, round(total_words / 500))

        return {
            '中文字数': chinese_chars,
            '英文单词数': english_words,
            '总字数': total_words,
            '句子数': sentences,
            '段落数': paragraphs,
            '预计阅读时间(分钟)': reading_time,
            '平均句长': round(total_words / sentences) if sentences > 0 else 0
        }

    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        提取关键词（简单的词频统计）
        """
        # 移除标点符号
        text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
        words = text.split()

        # 过滤停用词和短词
        filtered_words = [
            word for word in words
            if len(word) > 1 and word not in self.stop_words['中文'] and word not in self.stop_words['英文']
        ]

        # 统计词频
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # 返回前N个高频词
        return sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def check_readability(self, text: str) -> Dict:
        """
        检查文本可读性
        """
        analysis = self.analyze_text(text)

        # 计算可读性指标
        avg_sentence_length = analysis['平均句长']
        short_sentences = len([s for s in re.split(r'[。！？.!?]+', text) if len(s) < 20])
        long_sentences = len([s for s in re.split(r'[。！？.!?]+', text) if len(s) > 50])

        # 段落长度分析
        paragraphs = [p for p in text.split('\n') if p.strip()]
        short_paragraphs = len([p for p in paragraphs if len(p) < 50])
        long_paragraphs = len([p for p in paragraphs if len(p) > 200])

        # 计算可读性分数（简单版本）
        readability_score = 100
        if avg_sentence_length > 30:
            readability_score -= 10
        if long_sentences / analysis['句子数'] > 0.3:
            readability_score -= 10
        if long_paragraphs / analysis['段落数'] > 0.3:
            readability_score -= 10

        return {
            '可读性分数': max(0, readability_score),
            '平均句长': avg_sentence_length,
            '短句数量': short_sentences,
            '长句数量': long_sentences,
            '短段落数量': short_paragraphs,
            '长段落数量': long_paragraphs,
            '建议': self._get_readability_suggestions(avg_sentence_length, long_sentences, long_paragraphs)
        }

    def _get_readability_suggestions(self, avg_len: float, long_sents: int, long_paragraphs: int) -> List[str]:
        """
        获取可读性改进建议
        """
        suggestions = []

        if avg_len > 25:
            suggestions.append("句子过长，建议拆分长句")

        if long_sents > 5:
            suggestions.append("长句较多，考虑用短句增强表达力")

        if long_paragraphs > 3:
            suggestions.append("部分段落过长，可以分段提高可读性")

        if not suggestions:
            suggestions.append("文本可读性良好")

        return suggestions

    def generate_outline(self, topic: str, style: str = '标准') -> Dict:
        """
        生成文章大纲
        """
        outlines = {
            '标准': {
                '开头': [
                    '用有趣的故事或数据引入主题',
                    '提出核心观点或问题',
                    '预告文章结构'
                ],
                '主体': [
                    '分论点1：定义与背景',
                    '分论点2：具体案例或数据支撑',
                    '分论点3：方法论或实践建议',
                    '分论点4：常见误区及避免方法'
                ],
                '结尾': [
                    '总结核心观点',
                    '给出行动建议',
                    '引发读者思考或讨论'
                ]
            },
            '故事型': {
                '开头': [
                    '设置悬念或冲突',
                    '介绍故事背景',
                    '预示故事走向'
                ],
                '主体': [
                    '发展：遇到挑战',
                    '转折：关键决定或事件',
                    '高潮：突破或成长',
                    '结果：收获或感悟'
                ],
                '结尾': [
                    '提炼故事意义',
                    '分享经验教训',
                    '给读者启发'
                ]
            },
            '教程型': {
                '开头': [
                    '明确要解决的问题',
                    '说明学习这个技能的价值',
                    '展示最终效果'
                ],
                '主体': [
                    '步骤一：准备工作',
                    '步骤二：具体操作',
                    '步骤三：常见问题处理',
                    '步骤四：进阶技巧'
                ],
                '结尾': [
                    '总结关键要点',
                    '提供练习建议',
                    '推荐相关资源'
                ]
            }
        }

        return {
            '主题': topic,
            '风格': style,
            '大纲': outlines.get(style, outlines['标准']),
            '生成时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def suggest_titles(self, content: str, count: int = 5) -> List[str]:
        """
        根据内容建议标题
        """
        keywords = [word for word, freq in self.extract_keywords(content, 5)]

        title_templates = [
            f"关于{keywords[0] if keywords else '这个话题'}的深度思考",
            f"我是如何{keywords[1] if len(keywords) > 1 else '做到'}的",
            f"{keywords[0] if keywords else '这个'}：你应该知道的真相",
            f"从0到1掌握{keywords[2] if len(keywords) > 2 else '这个技能'}",
            f"关于{keywords[0] if keywords else '此事'}，我有话说"
        ]

        return title_templates[:count]

    def social_media_optimize(self, text: str, platform: str) -> Dict:
        """
        针对社交媒体平台优化建议
        """
        analysis = self.analyze_text(text)

        optimization_suggestions = {
            '微信公众号': {
                '标题建议': '标题要吸引点击，可以使用疑问句或数字',
                '长度建议': '文章长度建议在2000-3000字之间',
                '格式建议': '段落不宜过长，适当使用emoji增加亲和力',
                '互动建议': '结尾要有明确的互动引导（点赞、在看、留言）'
            },
            '微博': {
                '标题建议': '使用吸引眼球的标题，可以考虑热点话题',
                '长度建议': '正文控制在140字以内，重要信息前置',
                '格式建议': '使用#话题标签#，@相关用户',
                '互动建议': '使用提问或投票形式增加互动'
            },
            '小红书': {
                '标题建议': '标题要有emoji，突出痛点或爽点',
                '长度建议': '正文800-1500字，重点信息加粗或emoji标记',
                '格式建议': '内容分点，使用emoji作为标记',
                '互动建议': '结尾要有互动引导，使用相关话题标签'
            },
            '知乎': {
                '标题建议': '针对问题直接回答，开头亮明观点',
                '长度建议': '内容要有深度，逻辑清晰',
                '格式建议': '使用小标题分隔，适当使用加粗强调',
                '互动建议': '结尾可以引导读者关注或点赞'
            }
        }

        suggestions = optimization_suggestions.get(platform, optimization_suggestions['微信公众号'])

        return {
            '平台': platform,
            '当前分析': analysis,
            '优化建议': suggestions,
            '适配状态': self._check_platform_fit(analysis, platform)
        }

    def _check_platform_fit(self, analysis: Dict, platform: str) -> str:
        """
        检查内容与平台的匹配度
        """
        word_count = analysis['总字数']

        platform_requirements = {
            '微信公众号': (1000, 5000),
            '微博': (0, 140),
            '小红书': (500, 2000),
            '知乎': (800, 10000)
        }

        min_words, max_words = platform_requirements.get(platform, (1000, 3000))

        if word_count < min_words:
            return f"内容偏短，建议扩充到{min_words}字以上"
        elif word_count > max_words:
            return f"内容偏长，建议精简到{max_words}字以内"
        else:
            return "长度适中，符合平台要求"

def main():
    """
    命令行使用示例
    """
    helper = WritingHelper()

    print("=== AI写作助手工具 ===")
    print("1. 文本分析")
    print("2. 生成大纲")
    print("3. 建议标题")
    print("4. 社交媒体优化")
    print("5. 退出")

    while True:
        choice = input("\n请选择功能 (1-5): ")

        if choice == '1':
            print("\n请输入要分析的文本（输入完成后按回车）：")
            text = input()
            if text:
                analysis = helper.analyze_text(text)
                print("\n=== 文本分析结果 ===")
                for key, value in analysis.items():
                    print(f"{key}: {value}")

                readability = helper.check_readability(text)
                print(f"\n=== 可读性分析 ===")
                print(f"可读性分数: {readability['可读性分数']}")
                print("建议:")
                for suggestion in readability['建议']:
                    print(f"- {suggestion}")

        elif choice == '2':
            topic = input("\n请输入文章主题: ")
            print("可选风格: 标准, 故事型, 教程型")
            style = input("请选择风格 (默认标准): ") or "标准"

            outline = helper.generate_outline(topic, style)
            print(f"\n=== {topic} 文章大纲 ===")
            for section, points in outline['大纲'].items():
                print(f"\n【{section}】")
                for i, point in enumerate(points, 1):
                    print(f"{i}. {point}")

        elif choice == '3':
            print("\n请输入文章内容（用于生成标题）：")
            text = input()
            if text:
                titles = helper.suggest_titles(text)
                print("\n=== 建议标题 ===")
                for i, title in enumerate(titles, 1):
                    print(f"{i}. {title}")

        elif choice == '4':
            print("\n请输入文章内容：")
            text = input()
            print("可选平台: 微信公众号, 微博, 小红书, 知乎")
            platform = input("请选择平台: ")

            if text and platform:
                optimization = helper.social_media_optimize(text, platform)
                print(f"\n=== {platform} 优化建议 ===")
                for category, suggestions in optimization['优化建议'].items():
                    print(f"\n{category}:")
                    print(f"- {suggestions}")

                print(f"\n适配状态: {optimization['适配状态']}")

        elif choice == '5':
            print("感谢使用！")
            break

        else:
            print("无效选择，请重新输入")

if __name__ == "__main__":
    main()