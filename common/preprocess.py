"""
preprocess - 文本预处理（离线训练与在线推理共用）

单条文本级处理：正则清洗 → jieba 分词 → 去停用词

Author: 骆昊
Version: 0.0.1
"""
import html
import re

import jieba
import logging

import unicodedata

jieba.setLogLevel(logging.ERROR)


SPACE_PATTERN = re.compile(r'[\s\u3000]+')
BRACE_PATTERN = re.compile(r'\[.*?\]|\(.*?\)|【.*?】|（.*?）|「.*?」')
MYURL_PATTERN = re.compile(r'https?://[^\s\u4e00-\u9fa5]+')
TOPIC_PATTERN = re.compile(r'#.*?#')
CHENN_PATTERN = re.compile(r'[^a-zA-Z0-9\s\u4e00-\u9fa5:,.?!;：，。？！；]+')
NOENN_PATTERN = re.compile(r'[^\s\u4e00-\u9fa5：，。？！；]+')


def clean_text_for_bert(text: str, keep_emoji=False) -> str:
    """清洗文本内容（逐行）"""
    if not isinstance(text, str) or not text:
        return ''

    # 剔除 HTML 标签（包括脚本和样式表）
    text = html.unescape(text)
    text = re.sub(r'<script[\s\S]*?</script>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<style[\s\S]*?</style>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '', text)

    # 删除 Emoji 字符
    if not keep_emoji:
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)

    # Unicode 标准化（全角字符、圈号字符、特殊排版符号等）
    text = unicodedata.normalize('NFKC', text)

    # 删除控制字符和不可见字符
    cleaned_chars = []
    for char in text:
        # 获取字符的 Unicode 类别
        cat = unicodedata.category(char)
        if cat in ('Cc', 'Cf') and char not in ('\n', '\t'):
            continue
        cleaned_chars.append(char)
    text = ''.join(cleaned_chars)

    # 清理连续的空格和制表键
    text = re.sub(r'\t+', '\t', text)
    text = re.sub(' {2,}', ' ', text)

    return text.strip()
