"""Define which preview links are owned by the separate course publishing source."""
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import quote, unquote, urljoin, urlsplit, urlunsplit

ORIGIN = "https://xiongyingfei.github.io"
PREVIEW_MANIFEST = "assets/course-preview.json"
COURSE_ROOTS = {"SF", "SA_new", "SA", "DPPL"}


def course_directories(courses: dict) -> list[str]:
    directories = set()
    for course in courses.values():
        for offering in course.get("offerings", []):
            links = offering.get("link", "")
            for link in (links.values() if isinstance(links, dict) else [links]):
                url = urlsplit(link)
                if url.netloc or url.scheme:
                    continue
                parts = PurePosixPath(unquote(url.path).lstrip("/")).parts
                if len(parts) >= 2 and parts[0] in COURSE_ROOTS and re.fullmatch(r"\d{4}", parts[1]):
                    if int(parts[1]) != int(offering["year"]):
                        raise ValueError(f"data/courses.yaml：{offering['year']} 年的课程链接却指向 {parts[1]} 年，请核对年份。")
                    if ".." in parts or "\\" in url.path:
                        raise ValueError("data/courses.yaml：课程链接包含不安全的路径。")
                    directories.add("/".join(parts[:2]))
    return sorted(directories)


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        field = "src" if tag in {"img", "script"} else "href" if tag in {"a", "link"} else None
        if field and values.get(field):
            self.links.append(values[field])


def local_references(source: str, relative: str) -> set[str]:
    parser = References()
    parser.feed(source)
    result = set()
    for value in parser.links:
        url = urlsplit(urljoin(ORIGIN + "/" + relative, value))
        if url.scheme not in {"http", "https"} or url.netloc != urlsplit(ORIGIN).netloc:
            continue
        path = unquote(url.path).lstrip("/")
        if ".." not in PurePosixPath(path).parts and "\\" not in path:
            result.add(path)
    return result


def preview_manifest(out: Path) -> dict:
    path = out / PREVIEW_MANIFEST
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def remote_course_url(relative: str, manifest: dict) -> str | None:
    if not manifest.get("preview_only") or manifest.get("origin") != ORIGIN:
        return None
    url = urlsplit(relative)
    if url.scheme or url.netloc:
        return None
    path = unquote(url.path).lstrip("/")
    parts = PurePosixPath(path).parts
    if ".." in parts or "\\" in path:
        return None
    normalized = "/".join(parts)
    directory = "/".join(parts[:2])
    managed = directory in manifest.get("directories", [])
    shared = normalized in manifest.get("shared_files", [])
    if not managed and not shared:
        return None
    if (managed and len(parts) > 2 and int(parts[1]) < manifest["first_year"]
            and PurePosixPath(normalized).suffix.lower() in manifest["download_extensions"]):
        return None
    ending = "/" if url.path.endswith("/") and normalized else ""
    return urlunsplit(("https", urlsplit(ORIGIN).netloc, "/" + quote(normalized) + ending, url.query, url.fragment))
