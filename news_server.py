# news_server.py
# MCP Server - Berita Indonesia (Stabil + Fallback)
# Source: CNN Indonesia (utama) + Antara (fallback)

from mcp.server.fastmcp import FastMCP
import urllib.request
import re
import logging

logger = logging.getLogger("news_mcp")

mcp = FastMCP("BeritaIndonesia")

# ─── RSS Feed URLs (STABIL) ────────────────────────────────────────────────
FEEDS = {
    "nasional": [
        "https://rss.cnnindonesia.com/nasional",
        "https://www.antaranews.com/rss/terkini"
    ],
    "internasional": [
        "https://rss.cnnindonesia.com/internasional"
    ],
    "bisnis": [
        "https://rss.cnnindonesia.com/ekonomi"
    ],
    "teknologi": [
        "https://rss.cnnindonesia.com/teknologi"
    ],
    "olahraga": [
        "https://rss.cnnindonesia.com/olahraga"
    ],
    "terkini": [
        "https://rss.cnnindonesia.com/nasional"
    ],
}

# ─── FETCH RSS ─────────────────────────────────────────────────────────────
def fetch_rss(url: str) -> str:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception as e:
        logger.warning(f"Gagal fetch {url}: {e}")
        return ""

# ─── PARSE RSS ─────────────────────────────────────────────────────────────
def parse_rss(xml: str, max_items: int = 5):
    items = []
    for block in re.findall(r"<item>(.*?)</item>", xml, re.DOTALL):
        if len(items) >= max_items:
            break

        title = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block)
        desc  = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", block, re.DOTALL)

        if title:
            desc_text = ""
            if desc:
                desc_text = re.sub(r"<[^>]+>", "", desc.group(1)).strip()
                desc_text = desc_text[:160]

            items.append({
                "title": title.group(1).strip(),
                "description": desc_text
            })

    return items

# ─── MCP TOOL ─────────────────────────────────────────────────────────────
@mcp.tool()
def get_latest_news(category: str = "nasional", jumlah: int = 5) -> dict:
    """
    Ambil berita terbaru dari Indonesia.
    Gunakan tool ini saat user bertanya tentang berita, kabar terkini, atau informasi terbaru.

    Parameter:
    - category: nasional, internasional, bisnis, teknologi, olahraga, terkini
    - jumlah: jumlah berita (1-10)
    """

    cat = category.lower().strip()
    if cat not in FEEDS:
        cat = "nasional"

    count = max(1, min(int(jumlah), 10))
    urls = FEEDS[cat]

    logger.info(f"Fetching news: {cat}, count={count}")

    xml = ""
    for url in urls:
        xml = fetch_rss(url)
        if xml:
            logger.info(f"Berhasil ambil dari {url}")
            break

    if not xml:
        return {"success": False, "result": "Gagal mengambil berita (semua sumber error)."}

    items = parse_rss(xml, count)

    if not items:
        return {"success": False, "result": "Tidak ada berita ditemukan."}

    # ─── FORMAT OUTPUT (ENAK DIBACA VOICE) ───────────────────────────────
    lines = [f"Berita {cat.upper()} hari ini:"]

    for i, item in enumerate(items, 1):
        lines.append(f"{i}. {item['title']}")
        if item["description"]:
            lines.append(f"   {item['description']}")

    result_text = "\n".join(lines)

    logger.info(f"Return {len(items)} berita")
    return {"success": True, "result": result_text}


# ─── RUN SERVER ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")