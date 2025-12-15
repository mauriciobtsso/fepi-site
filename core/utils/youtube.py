# core/utils/youtube.py
import feedparser

FEPI_CHANNEL_ID = "UCm6mhuw6KC4AIy0OuxZqgiA"
FEED_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={FEPI_CHANNEL_ID}"

def get_latest_youtube_video_id() -> str | None:
    # User-Agent ajuda alguns provedores a não bloquearem request “genérico”
    feed = feedparser.parse(
        FEED_URL,
        request_headers={"User-Agent": "Mozilla/5.0 (FEPI Site)"},
    )

    # Se o parser detectar erro grave no feed, retorna None
    if getattr(feed, "bozo", 0):
        return None

    if not getattr(feed, "entries", None):
        return None

    entry = feed.entries[0]

    entry_id = entry.get("id", "") or ""
    if "yt:video:" in entry_id:
        return entry_id.split("yt:video:")[-1].strip()

    link = entry.get("link", "") or ""
    if "watch?v=" in link:
        return link.split("watch?v=")[-1].split("&")[0].strip()

    return None
