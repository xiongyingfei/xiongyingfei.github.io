"""After original Jekyll compilation, retain recent course downloads in the artifact only."""
from __future__ import annotations
import argparse
import hashlib
import html
from pathlib import Path
try:
    from course_retention import load_policy, inventory, finish
except ImportError:
    from scripts.course_retention import load_policy, inventory, finish

def notice(title: str, body: str) -> str:
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{html.escape(title)}</title><link rel="stylesheet" href="/assets/style.css">'
            '<link rel="stylesheet" href="/assets/theme.css"></head><body>'
            f'<main class="wrap" id="main"><div class="page-head"><h1>{html.escape(title)}</h1></div>'
            f'<div class="prose">{body}</div></main></body></html>')

def finalize(source: Path,site: Path,support: Path,year: int | None=None) -> dict:
    source,site,support=source.resolve(),site.resolve(),support.resolve()
    if site==source or not site.is_dir():
        raise ValueError("Expected a separate, existing Jekyll output directory")
    policy=load_policy(support,year)
    archived=inventory(site,policy)
    for relative in archived:
        path=site / relative
        if not path.resolve().is_relative_to(site):raise ValueError("Archive path escapes the artifact")
        path.unlink()
    for course,course_year in sorted({tuple(name.split("/")[:2]) for name in archived}):
        directory=site / course / course_year
        back=f"/{course}/{course_year}/" + ("index.html" if (directory/"index.html").exists() else "main.htm")
        body=(f'<p>仅提供近三年的课程胶片下载</p><p>当前保留 {policy.first_year}–{policy.year} 年的课程胶片。'
              '历史课程页面继续保留。</p>'
              f'<p><a href="{html.escape(back)}">返回课程页面</a> · <a href="/courses_cn.html">课程目录</a></p>')
        target=site / f"course-archive/{course}/{course_year}.html"
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(notice("仅提供近三年的课程胶片下载",body),encoding="utf-8")
    entries=[]
    for course in sorted(policy.roots):
        for directory in sorted((site/course).glob("*")):
            if directory.is_dir() and directory.name.isdigit() and policy.first_year <= int(directory.name) <= policy.year:
                page="index.html" if (directory/"index.html").exists() else "main.htm"
                if (directory/page).exists():
                    href=f"/{course}/{directory.name}/{page}"
                    entries.append(f'<li><a href="{href}">{course} {directory.name}</a></li>')
    text=f'<p>提供 {policy.first_year}–{policy.year} 年的课程胶片下载。</p><ul>'+"".join(entries)+'</ul><p><a href="/courses_cn.html">完整课程目录</a></p>'
    (site/"course-downloads.html").write_text(notice("近三年课程",text),encoding="utf-8")
    text=f'<p>仅提供近三年的课程胶片下载，当前范围为 {policy.first_year}–{policy.year} 年。</p><p><a href="/course-downloads.html">查看近三年课程</a> · <a href="/index_cn.html">返回主页</a></p><script src="/assets/archive-404.js" defer></script>'
    (site/"404.html").write_text(notice("页面不存在",text),encoding="utf-8")
    # Every retained source attachment must survive Jekyll and artifact pruning unchanged.
    failures=[]
    for folder in ["SF","SA","SA_new","DPPL","papers","slides","presentations","res","pics","_images"]:
        for path in (source/folder).rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".pdf",".ppt",".pptx",".doc",".docx",".zip",".7z",".gz"}:continue
            relative=path.relative_to(source).as_posix()
            if policy.archived(relative):continue
            dest=site / relative
            if not dest.is_file() or hashlib.sha256(path.read_bytes()).digest()!=hashlib.sha256(dest.read_bytes()).digest():
                failures.append(relative)
    if failures:raise ValueError("Retained source attachments missing or changed: "+", ".join(failures[:20]))
    (site / "assets").mkdir(exist_ok=True)
    result=finish(support,site,policy,archived)
    print("Original course sources preserved; only the generated publishing artifact was pruned")
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--site",type=Path,required=True)
    parser.add_argument("--support",type=Path,required=True)
    args=parser.parse_args()
    finalize(args.source,args.site,args.support)
