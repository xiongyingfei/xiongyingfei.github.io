"""Check generated routes, internal links, and publication anchors."""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
try:
    from course_sources import preview_manifest, remote_course_url
except ImportError:
    from scripts.course_sources import preview_manifest, remote_course_url


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        field = "src" if tag in {"img", "script"} else "href" if tag in {"a", "link"} else None
        if field and values.get(field):
            self.links.append(values[field])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", type=Path, default=Path(__file__).resolve().parents[1] / "dist")
    parser.add_argument("--preview", action="store_true", help="允许本地未缓存的已登记课程由预览服务打开线上原版；正式发布不要使用此选项")
    args = parser.parse_args()
    dist = args.dist.resolve()
    if not dist.is_dir():
        raise SystemExit("Build the site first")
    names = {f"{base}{suffix}.html" for base in (
        "index", "publications", "publications_by_type", "news", "presentations", "students", "awards", "services", "courses", "projects"
    ) for suffix in ("", "_cn")}
    generated = [dist / "styles.html", dist / "course-downloads.html", dist / "404.html", *dist.glob("course-archive/**/*.html"), *(dist / name for name in names), *dist.glob("publication/*.html"),
                 *dist.glob("SF/*/*.html"), *dist.glob("SA_new/*/*.html")]
    parsed: dict[Path, Links] = {}
    for page in generated:
        parser_instance = Links()
        parser_instance.feed(page.read_text(encoding="utf-8"))
        parsed[page.resolve()] = parser_instance
    problems: list[str] = []
    missing_targets: dict[str, list[str]] = {}
    legacy_warnings: list[str] = []
    routing = preview_manifest(dist) if args.preview else {}
    remote_references: set[str] = set()
    for page, document in parsed.items():
        is_course = page.relative_to(dist).parts[0] in {"SF", "SA_new"}
        if not is_course and "main" not in document.ids:
            problems.append(f"页面 {page.relative_to(dist)}：缺少正文区域标记 main，请检查页面模板。")
        for value in document.links:
            url = urlsplit(value)
            if url.scheme or url.netloc or value.startswith(("mailto:", "tel:", "data:", "javascript:")):
                continue
            target = (dist / unquote(url.path).lstrip("/")) if url.path.startswith("/") else (page.parent / unquote(url.path))
            if not url.path:
                target = page
            if not target.exists() and not target.suffix and target.with_suffix(".html").exists():
                target = target.with_suffix(".html")
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                relative = target.resolve().relative_to(dist).as_posix() if target.resolve().is_relative_to(dist) else ""
                if is_course and (url.path == "/feed.xml" or value == "slides/ex-3.pdf"):
                    legacy_warnings.append(f"{page.relative_to(dist)}: original missing {value}")
                elif args.preview and relative and remote_course_url(relative, routing):
                    remote_references.add(relative)
                else:
                    missing_targets.setdefault(value, []).append(page.relative_to(dist).as_posix())
            elif url.fragment and target.suffix.lower() in {".html", ".htm"}:
                target_resolved = target.resolve()
                if target_resolved in parsed and unquote(url.fragment) not in parsed[target_resolved].ids:
                    problems.append(f"页面 {page.relative_to(dist)}：找不到链接对应的页面位置（{value}）。")
    if problems or missing_targets:
        messages = list(problems)
        for target, pages in missing_targets.items():
            messages.append(f"链接目标不存在：{target}\n  引用页面：" + "、".join(dict.fromkeys(pages)))
        print("\n".join(messages[:100]))
        if any(re.match(r"/?(?:SF|SA_new|SA|DPPL)/\d{4}(?:/|$)", target) for target in missing_targets):
            print("建议：检查 data/courses.yaml 中的课程链接，并补齐对应课程页面或原课程预览缓存。")
        count = len(problems) + sum(len(pages) for pages in missing_targets.values())
        raise SystemExit(f"发现 {count} 处页面或链接问题，构建已停止。")
    if legacy_warnings:
        print(f"Preserved {len(legacy_warnings)} known original course references (feed.xml / missing ex-3.pdf)")
    if remote_references:
        print(f"预览说明：{len(remote_references)} 个课程页面或资源未缓存到本地；预览服务会打开线上原版。")
        for directory in sorted({"/".join(path.split("/")[:2]) for path in remote_references}):
            print(f"  {directory}：由发布仓库维护，正式发布时仍严格检查 Jekyll 编译结果。")
    print(f"Checked {len(parsed)} HTML pages and {sum(len(p.links) for p in parsed.values())} links")


if __name__ == "__main__":
    main()
