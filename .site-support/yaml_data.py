"""Read editable YAML with concise, source-aware maintenance errors."""
from pathlib import Path
import re

import yaml


class DataFileError(ValueError):
    """A data-file error that can be shown directly to the site maintainer."""


def display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return str(path)


def yaml_hint(error: yaml.YAMLError, lines: list[str]) -> str:
    problem = getattr(error, "problem", "") or ""
    context = getattr(error, "context", "") or ""
    mark = getattr(error, "problem_mark", None)
    if mark and mark.line < len(lines):
        current = lines[mark.line]
        indent = current[:len(current) - len(current.lstrip())]
        if "\t" in indent:
            return "缩进请使用空格，不要使用 Tab；同一级字段应保持相同缩进。"
        item = re.match(r"^(\s*)-\s+([^:]+):", current)
        # Only suggest an exact alignment when the parser was ending a mapping
        # and the same list key already exists at a smaller indentation.
        if item and "expected <block end>" in problem:
            for number in range(mark.line - 1, -1, -1):
                previous = re.match(r"^(\s*)-\s+([^:]+):", lines[number])
                if previous and previous[2] == item[2] and len(previous[1]) < len(item[1]):
                    difference = len(item[1]) - len(previous[1])
                    alignment = "顶格书写" if not previous[1] else f"保留 {len(previous[1])} 个前导空格"
                    return (f"这一条列表项应与第 {number + 1} 行的“- {item[2]}:”对齐；"
                            f"删掉行首多出的 {difference} 个空格，{alignment}。")
    if "quoted scalar" in context or "unexpected end of stream" in problem:
        return "检查前面文本的引号是否成对；英文单引号字符串中的单引号需要写成两个单引号。"
    if "could not find expected ':'" in problem:
        return "检查附近字段是否漏写冒号；请按“字段名: 内容”的格式填写。"
    if "mapping values are not allowed" in problem:
        return "检查前一行是否漏写冒号，以及字段冒号后是否有空格；正文含“冒号 + 空格”时，请用引号包住整个正文，或用 | 编写多行文本。"
    return "检查附近行的缩进、冒号和引号；同一级列表的“-”以及同一级字段应分别对齐。"


def load_yaml(path: Path):
    path = Path(path)
    try:
        source = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise DataFileError(
            f"文件编码错误\n文件：{display_path(path)}\n建议：在编辑器中将文件保存为 UTF-8 编码。"
        ) from error
    try:
        return yaml.safe_load(source)
    except yaml.YAMLError as error:
        lines = source.splitlines()
        mark = getattr(error, "problem_mark", None) or getattr(error, "context_mark", None)
        message = ["YAML 格式错误", f"文件：{display_path(path)}"]
        if mark:
            message.append(f"位置：第 {mark.line + 1} 行，第 {mark.column + 1} 列")
            message.append("")
            width = len(str(mark.line + 3))
            for number in range(max(0, mark.line - 2), min(len(lines), mark.line + 3)):
                prefix = f"{'>' if number == mark.line else ' '} {number + 1:>{width}} | "
                expanded = lines[number].expandtabs(4)
                caret = len(lines[number][:mark.column].expandtabs(4)) if number == mark.line else 0
                start = max(0, caret - 70)
                before = "…" if start else ""
                after = "…" if len(expanded) > start + 140 else ""
                message.append(prefix + before + expanded[start:start + 140] + after)
                if number == mark.line:
                    message.append(" " * (len(prefix) + len(before) + caret - start) + "^")
            if mark.line >= len(lines):
                message.append("  （文件结尾；请检查前一行或未闭合的引号）")
        message.extend(["", "建议：" + yaml_hint(error, lines)])
        raise DataFileError("\n".join(message)) from error
