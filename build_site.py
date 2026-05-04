#!/usr/bin/env python3
from __future__ import annotations

import html
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

import markdown as mdlib
import yaml

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
SITE_NAME = "ReiSearch Help Center"
SITE_DESC = "User guides, troubleshooting articles, and training documentation for ReiSearch."

CATEGORY_ORDER = [
    "Getting Started",
    "Troubleshooting",
    "Account & Settings",
    "Property Workspace",
    "Marketplace",
    "App Center",
    "Buy Boxes",
    "Documents & Images",
    "Comps & Analysis",
    "Network",
    "Presentations",
    "Tokens & Billing",
]


@dataclass
class Article:
    source: Path
    output: Path
    title: str
    description: str
    category: str
    section: str
    reading_time: str
    slug: str
    order: int
    body: str
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def clean_url(self) -> str:
        rel = self.output.relative_to(ROOT).as_posix()
        return "/" + rel.removesuffix(".html")


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not match:
        return {}, text
    raw_meta, body = match.groups()
    meta = yaml.safe_load(raw_meta) or {}
    return meta, body.lstrip("\n")


def strip_section(body: str, heading: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    i = 0
    target = heading.strip().lower()
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m and m.group(2).strip().lower() == target:
            level = len(m.group(1))
            i += 1
            while i < len(lines):
                nxt = lines[i]
                hm = re.match(r"^(#{1,6})\s+(.*)$", nxt)
                if hm and len(hm.group(1)) <= level:
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def strip_trailing_status(body: str) -> str:
    lines = [line for line in body.splitlines() if not re.match(r"^\*\*Status:\*\*\s*.*$", line.strip())]
    return "\n".join(lines)


def strip_leading_intro(body: str, description: str) -> str:
    lines = body.splitlines()
    if not lines:
        return body
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines):
        para = lines[i].strip()
        if para and normalize_key(para) == normalize_key(description):
            return "\n".join(lines[i + 1 :]).lstrip("\n")
    return body


def strip_leading_h1(body: str, title: str) -> str:
    lines = body.splitlines()
    out: list[str] = []
    removed = False
    for line in lines:
        if not removed:
            m = re.match(r"^#\s+(.*)$", line.strip())
            if m:
                heading = m.group(1).strip()
                if normalize_key(heading) == normalize_key(title):
                    removed = True
                    continue
        out.append(line)
    return "\n".join(out)



def strip_leading_generic_heading(body: str, headings: Iterable[str]) -> str:
    lines = body.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        return body
    m = re.match(r"^(#{1,6})\s+(.*)$", lines[i].strip())
    if not m:
        return body
    heading = m.group(2).strip()
    if normalize_key(heading) not in {normalize_key(h) for h in headings}:
        return body
    return "\n".join(lines[i + 1 :]).lstrip("\n")



def strip_leading_metadata_block(body: str) -> str:
    labels = {"title", "format", "audience", "slug", "purpose", "content", "status"}
    lines = body.splitlines()
    out: list[str] = []
    skipping = True
    for line in lines:
        stripped = line.strip()
        if skipping:
            if not stripped:
                continue
            match = re.match(r"^\*\*([^*]+):\*\*", stripped)
            if match and normalize_key(match.group(1)) in labels:
                continue
            skipping = False
        out.append(line)
    return "\n".join(out).lstrip("\n")


def first_paragraph(body: str) -> str:
    paragraphs = re.split(r"\n\s*\n", body.strip())
    for paragraph in paragraphs:
        text = paragraph.strip()
        if not text:
            continue
        if re.match(r"^(#{1,6})\s+", text):
            continue
        if text.startswith("[") and text.endswith("]"):
            continue
        if re.match(r"^\*\*[^*]+:\*\*", text):
            continue
        if re.match(r"^[A-Za-z][A-Za-z &/()-]*:\s*$", text):
            continue
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            return text
    return ""


def reading_time(body: str) -> str:
    words = len(re.findall(r"\b\w+\b", body))
    mins = max(1, math.ceil(words / 200))
    return f"{mins} min read"


def load_articles() -> list[Article]:
    articles: list[Article] = []
    for path in sorted(ARTICLES.rglob("*.md")):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        title = str(meta.get("title") or path.stem.replace("-", " ").title())
        description = str(meta.get("description") or "")
        category = str(meta.get("category") or path.parent.name.replace("-", " ").title())
        section = str(meta.get("section") or category)
        slug = str(meta.get("slug") or path.relative_to(ARTICLES).with_suffix("").as_posix())
        order = int(meta.get("order") or 999)
        reading = str(meta.get("readingTime") or reading_time(body))
        body = strip_leading_generic_heading(body, ["Help Content", "Overview", "Introduction"])
        body = strip_leading_metadata_block(body)
        hero_description = description.strip() or first_paragraph(body)
        if not description:
            description = hero_description
        clean_body = strip_trailing_status(strip_section(strip_section(strip_leading_intro(strip_leading_h1(body, title), hero_description), "Related articles"), "Need more help?"))
        articles.append(
            Article(
                source=path,
                output=path.with_suffix(".html"),
                title=title,
                description=description,
                category=category,
                section=section,
                reading_time=reading,
                slug=slug,
                order=order,
                body=clean_body,
                meta=meta,
            )
        )
    return articles


def build_lookup(articles: Iterable[Article]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for article in articles:
        lookup[normalize_key(article.title)] = article.clean_url
        lookup[normalize_key(article.slug)] = article.clean_url
        lookup[normalize_key(article.source.relative_to(ARTICLES).with_suffix("").as_posix())] = article.clean_url
    return lookup


def build_categories(articles: Iterable[Article]) -> list[dict[str, Any]]:
    categories: dict[str, list[Article]] = {}
    for article in articles:
        categories.setdefault(article.category, []).append(article)
    ordered = []
    seen = set()
    for name in CATEGORY_ORDER:
        if name in categories:
            ordered.append((name, categories[name]))
            seen.add(name)
    for name, items in sorted(categories.items(), key=lambda kv: kv[0]):
        if name not in seen:
            ordered.append((name, items))
    result = []
    for name, items in ordered:
        items = sorted(items, key=lambda a: (a.order, a.title))
        result.append(
            {
                "name": name,
                "count": len(items),
                "items": items,
                "slug": normalize_key(name),
            }
        )
    return result


def category_icon(category: str) -> str:
    slug = normalize_key(category)
    icons = {
        "getting-started": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 15c-1 1-2 4-2 4s3-1 4-2"/><path d="M9 15 4 10l6-1 5-5c2-2 5-1 5-1s1 3-1 5l-5 5-1 6-4-4Z"/><path d="M15 9h.01"/></svg>',
        "troubleshooting": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.7 6.3a4 4 0 0 0-5.6 5.6L3 18l3 3 6.1-6.1a4 4 0 0 0 5.6-5.6"/><path d="M15 5l4 4"/><path d="M18 2l4 4"/></svg>',
        "account-settings": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
        "property-workspace": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 10v11h14V10"/></svg>',
        "marketplace": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 10h16"/><path d="M5 10l1-6h12l1 6"/><path d="M6 10v10h12V10"/><path d="M9 20v-5h6v5"/></svg>',
        "app-center": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>',
        "buy-boxes": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8 12 3 3 8l9 5 9-5Z"/><path d="M3 8v8l9 5 9-5V8"/><path d="M12 13v8"/></svg>',
        "documents-images": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6"/><path d="M8 13h8"/><path d="M8 17h6"/></svg>',
        "comps-analysis": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19V5"/><path d="M4 19h16"/><path d="M8 16v-5"/><path d="M12 16V8"/><path d="M16 16v-7"/></svg>',
        "network": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>',
        "presentations": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20"/><path d="M4 7h16"/><path d="M4 17h16"/></svg>',
        "tokens-billing": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/><path d="M12 8v8"/><path d="M9 10.5c0-1.1 1.3-2 3-2s3 .9 3 2-1.3 2-3 2-3 .9-3 2 1.3 2 3 2 3-.9 3-2"/></svg>',
    }
    return icons.get(slug, '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="3"/></svg>')


def render_toc(tokens: list[dict[str, Any]]) -> str:
    if not tokens:
        return '<div class="toc-empty">No headings on this page.</div>'

    flat: list[tuple[int, dict[str, Any]]] = []

    def collect(nodes: list[dict[str, Any]], depth: int = 0) -> None:
        for node in nodes:
            flat.append((depth, node))
            collect(node.get("children") or [], depth + 1)

    collect(tokens)
    return "".join(
        '<a class="toc-item level-%s" href="#%s">%s</a>' % (min(depth, 3), node["id"], html.escape(node["name"]))
        for depth, node in flat
    )


def render_related_articles(article: Article, lookup: dict[str, str]) -> str:
    related = article.meta.get("relatedArticles") or []
    if not related:
        return ""
    cards = []
    for item in related:
        title = str(item.get("title") or "")
        slug = str(item.get("slug") or "")
        href = lookup.get(normalize_key(slug)) or lookup.get(normalize_key(title))
        label = "Read article →" if href else "Coming soon"
        card_inner = f'''<div class="related-kicker">Related</div>
              <div class="related-title">{html.escape(title)}</div>
              <div class="related-link">{label}</div>'''
        if href:
            cards.append(f'<a class="related-card" href="{html.escape(href)}">{card_inner}</a>')
        else:
            cards.append(f'<div class="related-card">{card_inner}</div>')
    return '<section class="related-section"><h2>Related articles</h2><div class="related-grid">' + "".join(cards) + "</div></section>"


def markdown_tokens(body: str) -> tuple[str, list[dict[str, Any]]]:
    renderer = mdlib.Markdown(extensions=["extra", "tables", "fenced_code", "toc"])
    html_body = renderer.convert(body)
    tokens = getattr(renderer, "toc_tokens", []) or []
    return html_body, tokens


SITE_CSS = """
*{box-sizing:border-box}html,body{margin:0;padding:0}body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#f7faff;color:#020617;line-height:1.5;min-height:100vh}a{color:inherit;text-decoration:none}button{font:inherit;cursor:pointer;border:0;background:none;color:inherit}img{max-width:100%;display:block}svg{display:block;flex-shrink:0}.shell{min-height:100vh}.header{position:sticky;top:0;z-index:40;border-bottom:1px solid rgba(226,232,240,.8);background:rgba(255,255,255,.92);backdrop-filter:blur(12px)}.header-inner,.page-inner,.home-inner{max-width:1500px;margin:0 auto}.header-inner{display:flex;align-items:center;gap:20px;padding:16px 24px}.brand{display:flex;align-items:center;gap:12px}.brand img{height:40px;width:auto}.brand-sub{font-size:14px;font-weight:600;color:#475569}.search{display:none;align-items:center;flex:1;max-width:520px;margin:0 auto;padding:12px 16px;border:1px solid #e2e8f0;border-radius:16px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.05)}@media(min-width:768px){.search{display:flex}}.search svg{width:16px;height:16px;color:#94a3b8;margin-right:12px}.search span{font-size:14px;color:#64748b}.visit-btn{display:none;margin-left:auto;padding:10px 16px;border-radius:12px;background:#2563eb;color:#fff;font-size:14px;font-weight:700;box-shadow:0 4px 6px -1px rgba(37,99,235,.2)}@media(min-width:768px){.visit-btn{display:inline-flex}}.avatar{width:36px;height:36px;border-radius:50%;background:#eff6ff;color:#1d4ed8;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800}.page-grid{display:grid;grid-template-columns:1fr;gap:20px;padding:24px}@media(min-width:1024px){.page-grid{grid-template-columns:280px minmax(0,1fr) 260px}}.sidebar,.rightbar{display:none}@media(min-width:1024px){.sidebar,.rightbar{display:block}}.sticky{position:sticky;top:96px}.card{border:1px solid #e2e8f0;border-radius:24px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.05)}.sidebar .card,.rightbar .card{overflow:hidden}.nav-group{padding:16px;border-bottom:1px solid #f1f5f9}.nav-group:last-child{border-bottom:0}.nav-title{display:flex;align-items:center;gap:12px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;font-weight:800;color:#475569}.nav-title svg{width:16px;height:16px;color:#2563eb}.nav-articles{margin-top:14px;padding-left:12px;border-left:1px solid #e2e8f0;display:flex;flex-direction:column;gap:6px}.nav-link{padding:8px 12px;border-radius:12px;font-size:14px;color:#475569}.nav-link:hover,.nav-link.active{background:#eff6ff;color:#1d4ed8;font-weight:700}.support{padding:16px}.support h3{margin:0 0 4px;font-size:14px}.support p{margin:0;font-size:14px;color:#475569}.support a{display:inline-flex;margin-top:16px;padding:10px 14px;border-radius:12px;border:1px solid #bfdbfe;background:#fff;color:#1d4ed8;font-weight:700}.article{min-width:0}.article-card{padding:24px;border:1px solid #e2e8f0;border-radius:24px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.05)}@media(min-width:768px){.article-card{padding:32px}}.breadcrumbs{display:flex;flex-wrap:wrap;align-items:center;gap:8px;font-size:14px;margin-bottom:20px}.breadcrumbs a{color:#1d4ed8;font-weight:600}.hero{display:grid;gap:24px;padding:28px;border:1px solid #bfdbfe;border-radius:24px;background:linear-gradient(135deg,#eff6ff,#fff,#eff6ff)}@media(min-width:768px){.hero{grid-template-columns:minmax(0,1fr) 220px;align-items:center}}.badge{display:inline-flex;padding:4px 12px;border-radius:999px;background:#dbeafe;color:#1d4ed8;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.06em}.hero h1{margin:18px 0 0;font-size:38px;line-height:1.08;letter-spacing:-.03em}@media(min-width:768px){.hero h1{font-size:52px}}.hero p{margin:14px 0 0;max-width:42rem;font-size:16px;line-height:1.75;color:#475569}.meta{display:flex;align-items:center;gap:8px;margin-top:20px;font-size:14px;color:#64748b}.hero-art{display:none;height:200px;border-radius:24px;background:#fff;border:1px solid #bfdbfe;box-shadow:0 10px 15px -3px rgba(37,99,235,.12);padding:20px}@media(min-width:768px){.hero-art{display:block}}.art-inner{height:100%;border:1px solid #dbeafe;border-radius:20px;background:linear-gradient(180deg,#fff,#eff6ff)}.content{margin-top:24px}.content h2,.content h3{letter-spacing:-.02em}.content h2{font-size:24px;margin:32px 0 12px}.content h3{font-size:18px;margin:24px 0 8px}.content p,.content li{font-size:16px;line-height:1.75;color:#334155}.content ul,.content ol{padding-left:24px}.content li{margin:8px 0}.content blockquote{margin:20px 0;padding:16px 18px;border-left:4px solid #93c5fd;background:#eff6ff;border-radius:16px;color:#1e3a8a}.content pre{overflow:auto;padding:16px;border-radius:16px;background:#0f172a;color:#e2e8f0}.content code{padding:2px 6px;border-radius:8px;background:#eef2ff;color:#3730a3}.content table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14px}.content th,.content td{border:1px solid #e2e8f0;padding:10px;text-align:left}.content th{background:#eff6ff}.content img{border-radius:18px;border:1px solid #e2e8f0;box-shadow:0 1px 2px rgba(0,0,0,.05)}.related-section,.feedback{margin-top:28px}.related-grid{display:grid;gap:14px;margin-top:14px}@media(min-width:768px){.related-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(min-width:1280px){.related-grid{grid-template-columns:repeat(4,minmax(0,1fr))}}.related-card{padding:16px;border:1px solid #e2e8f0;border-radius:18px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.05)}.related-kicker{font-size:12px;font-weight:800;text-transform:uppercase;color:#64748b}.related-title{margin-top:10px;font-size:14px;font-weight:800;color:#020617}.related-link{margin-top:14px;font-size:14px;font-weight:700;color:#1d4ed8}.feedback{display:flex;flex-direction:column;gap:16px;padding:18px;border:1px solid #e2e8f0;border-radius:18px;background:#f8fafc}@media(min-width:768px){.feedback{flex-direction:row;align-items:center;justify-content:space-between}}.feedback h3{margin:0}.feedback p{margin:4px 0 0;color:#475569}.feedback .buttons{display:flex;gap:12px}.feedback .buttons a{display:inline-flex;align-items:center;gap:8px;padding:10px 16px;border-radius:12px;border:1px solid #bfdbfe;background:#fff;color:#1d4ed8;font-weight:700}.toc{padding:18px}.toc h2{margin:0;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:#334155}.toc-list{display:flex;flex-direction:column;gap:10px;margin-top:14px;padding-left:12px;border-left:1px solid #e2e8f0}.toc-item{font-size:14px;color:#475569}.toc-item:hover{color:#1d4ed8}.toc-empty{margin-top:12px;font-size:14px;color:#64748b}.page-footer{max-width:1500px;margin:0 auto;padding:0 24px 48px;color:#64748b;font-size:14px}.notfound-wrap{min-height:100vh;display:grid;place-items:center;padding:24px}.notfound-card{max-width:720px;width:100%;padding:32px;border:1px solid #bfdbfe;border-radius:28px;background:#fff;box-shadow:0 10px 15px -3px rgba(37,99,235,.12);text-align:center}.notfound-card h1{margin:16px 0 0;font-size:42px;letter-spacing:-.03em}.notfound-card p{margin:12px auto 0;max-width:44rem;font-size:16px;line-height:1.75;color:#475569}.notfound-actions{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:24px}.notfound-actions a{display:inline-flex;padding:12px 18px;border-radius:12px;font-weight:700}.notfound-actions .primary{background:#2563eb;color:#fff}.notfound-actions .secondary{border:1px solid #bfdbfe;background:#fff;color:#1d4ed8}
"""


def render_article(article: Article, lookup: dict[str, str], categories: list[dict[str, Any]]) -> str:
    body_html, toc_tokens = markdown_tokens(article.body)
    related_html = render_related_articles(article, lookup)
    current_category = next((c for c in categories if c["name"] == article.category), None)
    nav_html = ""
    if current_category:
        links = "".join(
            f'<a class="nav-link{(" active" if item.title == article.title else "")}" href="{item.clean_url}">{html.escape(item.title)}</a>'
            for item in current_category["items"]
        )
        nav_html = (
            f'<div class="nav-group"><div class="nav-title">{category_icon(current_category["name"])}'
            f'{html.escape(current_category["name"])} <span style="margin-left:auto;color:#94a3b8">⌄</span></div>'
            f'<div class="nav-articles">{links}</div></div>'
        )
    category_list = "".join(
        f'<div class="nav-group"><div class="nav-title">{category_icon(cat["name"])}{html.escape(cat["name"])}'
        f'<span style="margin-left:auto;color:#94a3b8">{cat["count"]}</span></div></div>'
        for cat in categories
    )
    toc_html = render_toc(toc_tokens)
    video = article.meta.get("video") or {}
    video_title = html.escape(str(video.get("title") or article.title))
    video_duration = html.escape(str(video.get("duration") or article.reading_time))
    show_video = bool(video.get("title") or video.get("url") or video.get("duration"))
    hero_description = article.description.strip()
    hero_description_html = f'<p>{html.escape(hero_description)}</p>' if hero_description else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(article.title)} — {SITE_NAME}</title>
  <link rel="icon" href="/logo.png" />
  <style>{SITE_CSS}</style>
</head>
<body>
  <div class="shell">
    <header class="header">
      <div class="header-inner">
        <a class="brand" href="/">
          <img src="/logo.png" alt="ReiSearch" />
          <span class="brand-sub">Help Center</span>
        </a>
        <div class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.35-4.35"/></svg><span>Search help articles...</span></div>
        <a class="visit-btn" href="https://reisearch.com">Visit ReiSearch ↗</a>
        <div class="avatar">RS</div>
      </div>
    </header>

    <main class="page-grid">
      <aside class="sidebar">
        <div class="sticky card">
          {nav_html}
          <div class="nav-group">
            <div class="nav-title"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="3"/></svg>All categories</div>
          </div>
          {category_list}
        </div>
      </aside>

      <article class="article">
        <div class="article-card">
          <nav class="breadcrumbs"><a href="/">Help Center</a><span style="color:#94a3b8">/</span><span style="color:#64748b">{html.escape(article.category)}</span></nav>
          <section class="hero">
            <div>
              <span class="badge">{html.escape(article.category)}</span>
              <h1>{html.escape(article.title)}</h1>
              {hero_description_html}
              <div class="meta"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg><span>{html.escape(article.reading_time)}</span></div>
            </div>
            <div class="hero-art"><div class="art-inner" style="display:flex;align-items:center;justify-content:center;padding:24px"><div style="width:96px;height:96px;border-radius:28px;background:#eff6ff;color:#1d4ed8;display:flex;align-items:center;justify-content:center">{category_icon(article.category)}</div></div></div>
          </section>

          <div class="content">{body_html}</div>
          {related_html}
          {f'''<section class="feedback"><div><h3>Was this helpful?</h3><p>Your feedback helps us improve the help center.</p></div><div class="buttons"><a href="#">Yes</a><a href="#">No</a></div></section>''' if article.meta.get("showFeedback", True) else ""}
          {f'''<section class="feedback"><div><h3>Video walkthrough</h3><p>{video_title}</p></div><div class="buttons"><a href="#">Watch · {video_duration}</a></div></section>''' if show_video else ""}
        </div>
      </article>

      <aside class="rightbar">
        <div class="sticky card">
          <div class="toc">
            <h2>On this page</h2>
            <div class="toc-list">{toc_html}</div>
          </div>
          <div class="support"><h3>Still need help?</h3><p>Our support team is here for you.</p><a href="mailto:support@reisearch.com">Contact Support</a></div>
        </div>
      </aside>
    </main>

    <footer class="page-footer">Deployed at help.reisearch.com · Generated from markdown sources</footer>
  </div>
</body>
</html>
"""


def render_404() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>404 — {SITE_NAME}</title>
  <link rel="icon" href="/logo.png" />
  <style>{SITE_CSS}</style>
</head>
<body>
  <div class="notfound-wrap">
    <div class="notfound-card">
      <a class="brand" href="/" style="justify-content:center"><img src="/logo.png" alt="ReiSearch" /><span class="brand-sub">Help Center</span></a>
      <h1>Page not found</h1>
      <p>We couldn’t find that article. Try searching from the homepage or browse a category below.</p>
      <div class="notfound-actions">
        <a class="primary" href="/">Back to homepage</a>
        <a class="secondary" href="/articles/getting-started/01-creating-account">Start with Getting Started</a>
      </div>
    </div>
  </div>
</body>
</html>
"""


def main() -> None:
    articles = load_articles()
    lookup = build_lookup(articles)
    categories = build_categories(articles)
    for article in articles:
        article.output.write_text(render_article(article, lookup, categories), encoding="utf-8")
    (ROOT / "404.html").write_text(render_404(), encoding="utf-8")
    print(f"Generated {len(articles)} article pages and 404.html")


if __name__ == "__main__":
    main()
