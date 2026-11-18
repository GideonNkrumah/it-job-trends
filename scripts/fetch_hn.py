"""Hacker News: mine the monthly "Ask HN: Who is hiring?" thread."""
from __future__ import annotations

import html
import re

from common import http_json, log

STORY_SEARCH = (
    "https://hn.algolia.com/api/v1/search_by_date"
    "?tags=story,author_whoishiring&hitsPerPage=24"
)
COMMENT_SEARCH = (
    "https://hn.algolia.com/api/v1/search"
    "?tags=comment,story_{story_id}&hitsPerPage=1000&page={page}"
)
TAG_RE = re.compile(r"<[^>]+>")
HIRING_TITLE_RE = re.compile(r"^ask hn:\s*who is hiring\?", re.IGNORECASE)


def strip_html(raw):
    text = (raw or "").replace("<p>", "\n")
    text = re.sub(r"</p>|<br\s*/?>", "\n", text)
    text = TAG_RE.sub(" ", text)
    text = html.unescape(text)
    return re.sub(r"[ \t]+", " ", text).strip()


def _keyword_pattern(keyword):
    return re.compile(
        r"(?<![a-z0-9])" + re.escape(keyword.lower()) + r"(?![a-z0-9])", re.IGNORECASE
    )


def pick_story(stories_payload):
    hits = stories_payload.get("hits") or []
    candidates = [
        hit for hit in hits if HIRING_TITLE_RE.match((hit.get("title") or "").strip())
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda hit: int(hit.get("created_at_i") or 0))


def collect_comments(pages):
    comments = {}
    payloads = pages.values() if isinstance(pages, dict) else pages
    for payload in payloads:
        for hit in payload.get("hits") or []:
            object_id = hit.get("objectID")
            if object_id:
                comments[str(object_id)] = hit
    return list(comments.values())


def summarise(story, comments, cfg):
    section = cfg["hn"]
    min_length = int(section.get("min_text_length", 60))
    tracks = [
        (track["name"], [_keyword_pattern(word) for word in track["keywords"]])
        for track in section["tracks"]
    ]
    mentions = list(section.get("mentions") or [])
    mention_patterns = [_keyword_pattern(word) for word in mentions]

    posts = 0
    track_counts = {name: 0 for name, _ in tracks}
    mention_counts = {word: 0 for word in mentions}
    remote = 0

    for hit in comments:
        text = strip_html(hit.get("comment_text") or hit.get("story_text"))
        if len(text) < min_length:
            continue
        posts += 1
        lowered = text.lower()
        for name, patterns in tracks:
            if any(pattern.search(lowered) for pattern in patterns):
                track_counts[name] += 1
        for word, pattern in zip(mentions, mention_patterns):
            if pattern.search(lowered):
                mention_counts[word] += 1
        # HN convention: uppercase REMOTE marks remote-friendly roles.
        if re.search(r"\bREMOTE\b", text):
            remote += 1

    top_mentions = sorted(mention_counts.items(), key=lambda item: -item[1])[:12]
    return {
        "status": "ok",
        "story_id": str(story.get("objectID")),
        "story_title": story.get("title"),
        "thread_url": "https://news.ycombinator.com/item?id=%s" % story.get("objectID"),
        "posted_at": story.get("created_at"),
        "comments_indexed": len(comments),
        "posts": posts,
        "tracks": dict(sorted(track_counts.items(), key=lambda item: -item[1])),
        "mentions": dict((word, count) for word, count in top_mentions if count),
        "remote_share": round(remote / posts, 3) if posts else None,
    }


def parse(stories_payload, comment_pages, cfg):
    story = pick_story(stories_payload or {})
    if story is None:
        return {"status": "error", "reason": "no 'Who is hiring?' story found"}
    return summarise(story, collect_comments(comment_pages or {}), cfg)


def fetch(cfg, fixture=None):
    if fixture is not None:
        return parse(
            fixture.get("stories") or {},
            fixture.get("comments") or {},
            cfg,
        )

    stories_payload = http_json(STORY_SEARCH)
    story = pick_story(stories_payload)
    if story is None:
        return {"status": "error", "reason": "no 'Who is hiring?' story found"}

    story_id = story["objectID"]
    pages = {}
    max_pages = int(cfg["hn"].get("max_pages", 3))
    for page in range(max_pages):
        payload = http_json(COMMENT_SEARCH.format(story_id=story_id, page=page))
        pages[str(page)] = payload
        total_pages = int(payload.get("nbPages") or 0)
        if page + 1 >= total_pages:
            break
    log("hn: story %s, %s comment pages fetched" % (story_id, len(pages)))
    return parse(stories_payload, pages, cfg)
