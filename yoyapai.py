#!/usr/bin/env python3
"""抓取 yoyapai.com 最新日期的免费 Clash 订阅并保存为 yoyapai.yaml。

流程：
1. 请求“免费节点分享”分类页，取列表中最新的文章（不要求是当天）；
2. 请求文章页，定位 Clash 订阅代码块中的 .yaml 地址；
3. 下载订阅内容，原子写入 yoyapai.yaml。
"""

from __future__ import annotations

import argparse
import html
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

CATEGORY_URL = "https://yoyapai.com/category/mianfeijiedian"
DEFAULT_OUTPUT = "yoyapai.yaml"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
}

POST_HEADING_RE = re.compile(r"<h[23]\b[^>]*>(.*?)</h[23]>", re.IGNORECASE | re.DOTALL)
ANCHOR_RE = re.compile(
    r"""<a\b[^>]*?\bhref\s*=\s*["']([^"']+)["'][^>]*>(.*?)</a>""",
    re.IGNORECASE | re.DOTALL,
)
HEADING_RE = re.compile(r"<h[1-6]\b[^>]*>(.*?)</h[1-6]>", re.IGNORECASE | re.DOTALL)
PRE_RE = re.compile(r"<pre\b[^>]*>(.*?)</pre>", re.IGNORECASE | re.DOTALL)
CODE_RE = re.compile(r"<code\b[^>]*>(.*?)</code>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]*>")
DATE_RE = re.compile(r"(\d{1,2})\s*月\s*(\d{1,2})\s*日")
URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")

CLASH_CONFIG_MARKERS = ("proxies:", "proxy-providers:", "proxy-groups:", "mixed-port:")


class CrawlError(RuntimeError):
    """抓取过程中的可预期错误。"""


@dataclass(frozen=True)
class Post:
    title: str
    url: str


def clean_text(fragment: str) -> str:
    """去掉 HTML 标签、反转义实体并压缩空白。"""
    return WHITESPACE_RE.sub(" ", html.unescape(TAG_RE.sub("", fragment))).strip()


def parse_posts(page_html: str) -> list[Post]:
    """从分类页中解析出文章标题和链接。"""
    posts: list[Post] = []
    seen: set[str] = set()

    for heading in POST_HEADING_RE.finditer(page_html):
        anchor = ANCHOR_RE.search(heading.group(1))
        if not anchor:
            continue

        title = clean_text(anchor.group(2))
        if not title or not DATE_RE.search(title):
            continue

        url = urljoin(CATEGORY_URL, html.unescape(anchor.group(1)).strip())
        parsed = urlparse(url)
        if (parsed.hostname or "").lower() not in {"yoyapai.com", "www.yoyapai.com"}:
            continue
        if not parsed.path.strip("/").isdigit() or url in seen:
            continue

        seen.add(url)
        posts.append(Post(title=title, url=url))

    return posts


def latest_post(posts: list[Post]) -> Post:
    """返回最新日期的文章；分类页按发布时间倒序，第一篇即最新。"""
    if not posts:
        raise CrawlError("未能从分类页解析出文章，页面结构可能已变化")
    return posts[0]


def is_yaml_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and parsed.path.lower().endswith((".yaml", ".yml"))


def extract_clash_subscription_url(page_html: str) -> str:
    """从文章页中提取 Clash 订阅地址（.yaml）。"""
    text = html.unescape(page_html)

    # 优先读取“Clash ... 订阅地址”标题后的第一个代码块。
    for heading in HEADING_RE.finditer(text):
        heading_text = clean_text(heading.group(1)).lower()
        if "clash" not in heading_text or "订阅" not in heading_text:
            continue

        block = PRE_RE.search(text[heading.end() :])
        if not block:
            continue

        code = CODE_RE.search(block.group(1))
        content = clean_text(code.group(1) if code else block.group(1))
        match = URL_RE.search(content)
        if match and is_yaml_url(match.group(0)):
            return match.group(0)

    # 页面结构变化时兜底：全文查找 .yaml 链接，优先带 clash 的地址。
    yaml_urls: list[str] = []
    for url in URL_RE.findall(text):
        if is_yaml_url(url) and url not in yaml_urls:
            yaml_urls.append(url)
    for url in yaml_urls:
        if "clash" in url.lower():
            return url
    if yaml_urls:
        return yaml_urls[0]

    raise CrawlError("文章页中未找到 Clash 订阅地址（.yaml）")


def build_session() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.headers.update(HEADERS)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def request(session: requests.Session, url: str, *, referer: str | None = None) -> requests.Response:
    headers = {"Referer": referer} if referer else None
    try:
        response = session.get(url, headers=headers, timeout=(10, 90))
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CrawlError(f"请求失败：{url}\n  {exc}") from exc
    return response


def fetch_html(session: requests.Session, url: str, *, referer: str | None = None) -> str:
    response = request(session, url, referer=referer)
    try:
        # 站点会错误地声明 charset=iso-8859-1，这里强制按 UTF-8 解码。
        return response.content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CrawlError(f"响应不是有效的 UTF-8：{url}") from exc


def fetch_subscription(session: requests.Session, url: str, *, referer: str) -> bytes:
    response = request(session, url, referer=referer)
    data = response.content

    if not data.strip():
        raise CrawlError("订阅地址返回了空内容")

    preview = data[:1024].lstrip().lower()
    if preview.startswith((b"<!doctype html", b"<html")) or b"<head" in preview[:512]:
        raise CrawlError("订阅地址返回了 HTML 页面，可能被站点拦截")

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CrawlError("订阅内容不是有效的 UTF-8") from exc

    if not any(marker in text for marker in CLASH_CONFIG_MARKERS):
        raise CrawlError("下载内容不像 Clash 配置（缺少 proxies 等字段）")

    return data


def save_atomic(path: Path, data: bytes) -> None:
    """先写临时文件再替换，避免留下半截的 yoyapai.yaml。"""
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".part", dir=str(path.parent)
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as file:
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, path)
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="抓取 yoyapai.com 最新日期的 Clash 免费订阅并保存为 YAML。"
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"输出文件路径（默认：{DEFAULT_OUTPUT}）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = Path(args.output)
    session = build_session()

    print(f"[1/3] 获取分类页：{CATEGORY_URL}")

    try:
        category_html = fetch_html(session, CATEGORY_URL)
        posts = parse_posts(category_html)
        post = latest_post(posts)

        print(f"[2/3] 最新文章：{post.title}")
        print(f"      链接：{post.url}")

        article_html = fetch_html(session, post.url, referer=CATEGORY_URL)
        subscription_url = extract_clash_subscription_url(article_html)
        print(f"      订阅：{subscription_url}")

        print("[3/3] 下载 Clash 订阅内容 ...")
        data = fetch_subscription(session, subscription_url, referer=post.url)
        save_atomic(output, data)
    except CrawlError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        return 130

    print(f"完成：{output.resolve()}（{len(data):,} 字节）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
