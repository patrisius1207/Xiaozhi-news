# news_server.py
# MCP Server - Google News Indonesia (STABIL)

from mcp.server.fastmcp import FastMCP
import urllib.request
import re
import logging

logger = logging.getLogger("news_mcp")

mcp = FastMCP("GoogleNewsIndonesia")

# ─── GOOGLE NEWS RSS ─────────────────────────────────────────────
FEEDS = {
    "terkini": "https://news.google.com/rss?hl=id&gl=ID&ceid=ID:id",
    "nasional": "https://news.google.com/rss/search?q=indonesia&hl=id&gl=ID&ceid=ID:id",
    "teknologi": "https://news.google.com/rss/search?q=teknologi&hl=id&gl=ID&ceid=ID:id",
    "bisnis": "https://news.google.com/rss/search?q=bisnis&hl=id&gl=ID&ceid=ID:id",
    "olahraga": "https://news.google.com/rss/search?q=olahraga&hl=id&gl=ID&ceid=ID:id",
    "internasional": "https://news.google.com/rss/search?q=internasional&hl=id&gl=ID&ceid=ID:id",
}

# ─── FETCH ──────────────────────────────────────────────────────
def fetch_rss(url: str) -> str:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return ""

# ─── PARSE ──────────────────────────────────────────────────────
def parse_rss(xml: str, max_items: int = 5):
    items = []

    for block in re.findall(r"<item>(.*?)</item>", xml, re.DOTALL):
        if len(items) >= max_items:
            break

        title = re.search(r"<title>(.*?)</title>", block)
        source = re.search(r"<source.*?>(.*?)</source>", block)

        if title:
            items.append({
                "title": title.group(1).strip(),
                "source": source.group(1).strip() if source else ""
            })

    return items

# ─── TOOL ───────────────────────────────────────────────────────
@mcp.tool()
def get_latest_news(category: str = "terkini", jumlah: int = 5) -> dict:
    """
    Ambil berita terbaru dari Google News Indonesia.
    Gunakan saat user bertanya tentang berita, kabar terbaru, atau topik tertentu.
    """

    cat = category.lower().strip()
    if cat not in FEEDS:
        cat = "terkini"

    count = max(1, min(int(jumlah), 10))
    url = FEEDS[cat]

    logger.info(f"Fetching Google News: {cat}")

    xml = fetch_rss(url)
    if not xml:
        return {"success": False, "result": "Gagal mengambil berita."}

    items = parse_rss(xml, count)

    if not items:
        return {"success": False, "result": "Tidak ada berita ditemukan."}

    # ─── FORMAT OUTPUT (VOICE FRIENDLY) ─────────────────────────
    lines = [f"Berita {cat.upper()} terbaru dari Google News:"]

    for i, item in enumerate(items, 1):
        if item["source"]:
            lines.append(f"{i}. {item['title']} ({item['source']})")
        else:
            lines.append(f"{i}. {item['title']}")

    result_text = "\n".join(lines)

    return {"success": True, "result": result_text}


if __name__ == "__main__":
    mcp.run(transport="stdio")