"""Build-time course download retention. Never deletes or edits source assets."""
from __future__ import annotations

import html
import json
import posixpath
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urljoin, urlsplit

try:
    from yaml_data import load_yaml
except ImportError:
    from scripts.yaml_data import load_yaml


@dataclass(frozen=True)
class Policy:
    year: int
    retain_years: int
    roots: frozenset[str]
    extensions: frozenset[str]
    hosts: frozenset[str]
    warning_bytes: int
    budget_bytes: int

    @property
    def first_year(self) -> int:
        return self.year - self.retain_years + 1

    def archived(self, path: str) -> bool:
        parts = PurePosixPath(path).parts
        return (len(parts) >= 3 and parts[0] in self.roots
                and bool(re.fullmatch(r"\d{4}", parts[1]))
                and int(parts[1]) < self.first_year
                and PurePosixPath(path).suffix.lower() in self.extensions)


def load_policy(root: Path, year: int | None = None) -> Policy:
    data = load_yaml(root / "data/publishing.yaml")
    rules = data["course_downloads"]
    year = year if year is not None else datetime.now(timezone(timedelta(hours=8))).year
    roots = frozenset(rules["roots"])
    extensions = frozenset("." + ext.lower().lstrip(".") for ext in rules["excluded_extensions"])
    if not roots or not roots <= {"DPPL", "SA", "SA_new", "SF"}:
        raise ValueError("Retention roots must be known course directories; papers/presentations are protected")
    if not extensions or not extensions <= {".pdf", ".ppt", ".pptx"}:
        raise ValueError("Retention may only exclude course PDF/PPT/PPTX")
    years = rules["retain_years"]
    if not isinstance(years, int) or not 1 <= years <= 100 or not 2000 <= year <= 9999:
        raise ValueError("Invalid retention year/window")
    warning, budget = int(data["size_warning_bytes"]), int(data["size_budget_bytes"])
    if not 0 < warning <= budget:
        raise ValueError("Invalid publishing size budget")
    return Policy(year, years, roots, extensions, frozenset(data["site_hosts"]), warning, budget)


def notice_path(path: str) -> str:
    course, year, *_ = PurePosixPath(path).parts
    return f"course-archive/{course}/{year}.html"


def inventory(static: Path, policy: Policy) -> dict[str, dict]:
    return {p.relative_to(static).as_posix(): {"bytes": p.stat().st_size,
            "notice": notice_path(p.relative_to(static).as_posix())}
            for p in sorted(static.rglob("*")) if p.is_file() and policy.archived(p.relative_to(static).as_posix())}


def local_target(value: str, page: str, policy: Policy) -> str | None:
    url = urlsplit(value.strip())
    if url.scheme and url.scheme.lower() not in {"http", "https"}:
        return None
    if url.netloc and url.hostname not in policy.hosts:
        return None
    resolved = urlsplit(urljoin("https://retention.invalid/" + page, value.strip()))
    return posixpath.normpath(unquote(resolved.path)).lstrip("/")


ATTRIBUTE = re.compile(r'''(?P<prefix>\b(?:href|src|data)\s*=\s*)(?P<value>"[^"]*"|'[^']*'|[^\s>]+)''', re.I)
DOWNLOAD = re.compile(r'''\s+download(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?(?=\s|/?>)''', re.I)


class Rewriter(HTMLParser):
    def __init__(self, source: str, page: str, policy: Policy, archived: dict):
        super().__init__(convert_charrefs=False)
        self.source, self.page, self.policy, self.archived = source, page, policy, archived
        self.offsets = [0]
        for line in source.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.edits: list[tuple[int, int, str]] = []
        self.replacements = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag not in {"a", "area", "iframe", "embed", "object"}:
            return
        raw = self.get_starttag_text()
        changed = False
        def replace(match):
            nonlocal changed
            raw_value = match["value"]
            value = html.unescape(raw_value[1:-1] if raw_value[:1] in {'"', "'"} else raw_value)
            target = local_target(value, self.page, self.policy)
            if target not in self.archived:
                return match[0]
            changed = True
            self.replacements += 1
            return match["prefix"] + '"/' + self.archived[target]["notice"] + '"'
        updated = ATTRIBUTE.sub(replace, raw)
        if changed:
            updated = DOWNLOAD.sub("", updated)
            line, column = self.getpos()
            start = self.offsets[line - 1] + column
            self.edits.append((start, start + len(raw), updated))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def rewritten(self) -> str:
        text = self.source
        for start, end, replacement in reversed(self.edits):
            text = text[:start] + replacement + text[end:]
        return text


def read_html(path: Path) -> tuple[str, str]:
    raw = path.read_bytes()
    for encoding in ["utf-8", "gb18030"]:
        try:
            return raw.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    raise ValueError(f"Unsupported HTML encoding: {path}")


def rewrite_downloads(out: Path, policy: Policy, archived: dict) -> dict:
    pages, links = 0, 0
    for path in sorted(out.rglob("*")):
        if path.suffix.lower() not in {".html", ".htm"}:
            continue
        source, encoding = read_html(path)
        parser = Rewriter(source, path.relative_to(out).as_posix(), policy, archived)
        parser.feed(source)
        if parser.edits:
            # Output assets may be hardlinked to static/. Break the link first.
            replacement = path.with_name(path.name + ".retention-tmp")
            replacement.write_bytes(parser.rewritten().encode(encoding))
            replacement.replace(path)
            pages += 1
            links += parser.replacements
    return {"pages": pages, "links": links}


def verify(root: Path, out: Path, policy: Policy, archived: dict) -> None:
    problems = []
    for relative, item in archived.items():
        if (out / relative).exists():
            problems.append(f"Archived attachment leaked into output: {relative}")
        if not (out / item["notice"]).is_file():
            problems.append(f"Missing archive notice: {item['notice']}")
    for source_root, output_prefix in [(root / "static", ""), (root / "papers", "papers"), (root / "presentations", "presentations")]:
        for path in source_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".pdf", ".ppt", ".pptx", ".doc", ".docx", ".zip", ".7z", ".gz"}:
                continue
            relative = path.relative_to(source_root).as_posix()
            target = "/".join(part for part in [output_prefix, relative] if part)
            if source_root == root / "static" and relative in archived:
                continue
            dest = out / target
            if not dest.is_file() or dest.stat().st_size != path.stat().st_size:
                problems.append(f"Retained attachment missing or changed: {target}")
    for path in out.rglob("*"):
        if path.is_file() and policy.archived(path.relative_to(out).as_posix()):
            problems.append(f"Expired course file still present: {path.relative_to(out)}")
        if path.suffix.lower() in {".htm", ".html"}:
            source, _ = read_html(path)
            parser = Rewriter(source, path.relative_to(out).as_posix(), policy, archived)
            parser.feed(source)
            if parser.replacements:
                problems.append(f"Unrewritten archived links in {path.relative_to(out)}")
    if problems:
        raise ValueError("\n".join(problems[:30]))


def finish(root: Path, out: Path, policy: Policy, archived: dict) -> dict:
    rewrites = rewrite_downloads(out, policy, archived)
    manifest = {"first_year": policy.first_year, "year": policy.year,
                "files": {path: "/" + entry["notice"] for path, entry in archived.items()}}
    (out / "assets/course-archive.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    verify(root, out, policy, archived)
    size = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
    report = {"year": policy.year, "first_year": policy.first_year,
              "excluded_count": len(archived), "excluded_bytes": sum(x["bytes"] for x in archived.values()),
              "output_bytes": size, "warning_bytes": policy.warning_bytes, "budget_bytes": policy.budget_bytes,
              "rewrites": rewrites, "excluded_files": archived}
    reports = root / "reports"
    reports.mkdir(exist_ok=True)
    (reports / "publishing.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Course downloads: {policy.first_year}-{policy.year}; excluded {len(archived)} old files "
          f"({report['excluded_bytes'] / 1e6:.1f} MB); rewrote {rewrites['links']} links")
    print(f"Publishing size: {size / 1e6:.1f} MB; budget {policy.budget_bytes / 1e6:.0f} MB; report: reports/publishing.json")
    if size > policy.budget_bytes:
        raise ValueError("Publishing size exceeds configured budget; deployment must stop")
    if size > policy.warning_bytes:
        print("WARNING: publishing size is approaching the configured budget")
    return report
