# core/utils/youtube.py
import feedparser

DEFAULT_USER_AGENT = "Mozilla/5.0 (FEPI Site)"

def get_latest_youtube_video_id(channel_id: str, user_agent: str = DEFAULT_USER_AGENT) -> str | None:
    """
    Retorna o ID do vídeo mais recente de um canal do YouTube via RSS (sem API Key).
    channel_id: ex "UCxxxx..."
    """
    channel_id = (channel_id or "").strip()
    if not channel_id:
        return None

    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"

    feed = feedparser.parse(
        feed_url,
        request_headers={"User-Agent": user_agent},
    )

    if getattr(feed, "bozo", 0):
        return None

    if not getattr(feed, "entries", None):
        return None

    entry = feed.entries[0]

    entry_id = (entry.get("id", "") or "").strip()
    if "yt:video:" in entry_id:
        return entry_id.split("yt:video:")[-1].strip() or None

    link = (entry.get("link", "") or "").strip()
    if "watch?v=" in link:
        return link.split("watch?v=")[-1].split("&")[0].strip() or None

    return None
