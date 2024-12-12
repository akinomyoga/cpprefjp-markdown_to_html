# -*- coding: utf-8 -*-
"""
表示崩れを事前修正
=========================================

Markdownライブラリの以下の制限を回避：

- 箇条書きの前に空行が必要な制限を回避して、自動で空行を挟む
"""

import re
import datetime

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

def is_item_line(line: str) -> bool:
    stripped_line = line.strip()
    m = re.match(r'^([0-9]+\.\s)', stripped_line)
    if m:
        return True

    m = re.match(r'^([*+-]\s)', stripped_line)
    if m:
        return True
    return False

def is_item_end_line(line: str) -> bool:
    if len(line) == 0:
        return True
    if re.match(r'^#+ ', line):
        return True
    return False

def indent_level(line: str) -> int:
    m = re.match(r'^\s+', line)
    if m:
        return len(m.group(0).replace('\t', '    '))
    return 0

class FixDisplayErrorExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        pre = FixDisplayErrorPreprocessor(md)

        md.registerExtension(self)
        md.preprocessors.register(pre, 'fix_display_error', 28)


class FixDisplayErrorPreprocessor(Preprocessor):

    def __init__(self, md):
        Preprocessor.__init__(self, md)

    def run(self, lines):
        new_lines = []

        prev_line: str | None = None
        prev_line_is_item: bool = False
        in_item: bool = False
        paragraph_item_indent_level: int = 0
        for line in lines:
            if prev_line == None:
                prev_line = line
                new_lines.append(line)
                continue

            line_is_item: bool = is_item_line(line)
            if line_is_item:
                if not (prev_line_is_item or in_item):
                    new_lines.append("")
                elif in_item and indent_level(line) < paragraph_item_indent_level:
                    new_lines.append("")

                if not in_item:
                    paragraph_item_indent_level = indent_level(line)

                in_item = True

            elif in_item and is_item_end_line(line):
                in_item = False

            prev_line = line
            prev_line_is_item = line_is_item
            new_lines.append(line)

        return new_lines


def makeExtension(**kwargs):
    return FixDisplayErrorExtension(**kwargs)
