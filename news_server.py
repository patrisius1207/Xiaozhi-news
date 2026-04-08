# news_server.py
# MCP Server - Berita Terbaru dari Kompas.com & Antara
# Untuk XiaoZhi ESP32
#
# Cara jalankan:
#   pip install -r requirements.txt
#   export MCP_ENDPOINT=wss://api.xiaozhi.me/mcp/?token=...
#   python mcp_pipe.py news_server.py

from mcp.server.fastmcp import FastMCP
import urllib.request
import re
import logging

logger = logging.getLogger("news_mcp")

mcp = FastMCP("BeritaIndonesia")

# ─── RSS Feed URLs ────────────────────────────────────────────────────────────
FEEDS = {
    "nasional":      "https://www.antaranews.com/rss/nasional.xml",
    "internasional": "https://www.antaranews.com/rss/internasional.xml",
    "bisnis":        "https://www.antaranews.com/rss/ekonomi.xml",
    "teknologi":     "https://www.antaranews.com/rss/tekno.xml",
    "olahraga":      "https://www.antaranews.com/rss/olahraga.xml",
    "terkini":       "https://www.antaranews.com/rss/terkini.xml",
}

def fetch_rss(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "XiaoZhiNewsBot/1.0"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def parse_rss(xml: str, max_items: int = 5) -> list[dict]:
    items = []
    for block in re.findall(r"<item>(.*?)</item>", xml, re.DOTALL):
        if len(items) >= max_items:
            break
        title = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", block)
        desc  = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", block, re.DOTALL)
        pub   = re.search(r"<pubDate>(.*?)</pubDate>", block)
        if title:
            desc_text = ""
            if desc:
                desc_text = re.sub(r"<[^>]+>", "", desc.group(1)).strip()
                desc_text = desc_text[:180]
            items.append({
                "title": title.group(1).strip(),
                "description": desc_text,
                "date": pub.group(1).strip() if pub else "",
            })
    return items


@mcp.tool()
def get_latest_news(
    category: str = "nasional",
    jumlah: int = 5
) -> dict:
    """
    Ambil berita terbaru dari Kompas.com atau Antara News.
    Gunakan tool ini setiap kali pengguna bertanya tentang berita terkini,
    kabar hari ini, kejadian terbaru, atau informasi aktual.

    Parameter:
    - category: kategori berita. Pilihan: nasional, internasional, bisnis,
                teknologi, olahraga, terkini (Antara). Default: nasional.
    - jumlah: berapa berita yang ingin ditampilkan (1-10). Default: 5.

    Contoh: jika pengguna bilang "ada berita apa hari ini?", gunakan category=nasional.
    Jika tanya "berita teknologi terbaru?", gunakan category=teknologi.
    """
    cat = category.lower().strip()
    if cat not in FEEDS:
        cat = "nasional"

    count = max(1, min(int(jumlah), 10))
    url = FEEDS[cat]

    logger.info(f"Fetching news: category={cat}, count={count}, url={url}")

    try:
        xml = fetch_rss(url)
        items = parse_rss(xml, count)

        if not items:
            return {"success": False, "result": "Tidak ada berita ditemukan."}

        sumber = "Antara News" if cat == "terkini" else "Kompas.com"
        lines = [f"Berita {cat.upper()} terbaru dari {sumber}:"]
        for i, item in enumerate(items, 1):
            lines.append(f"\n{i}. {item['title']}")
            if item["description"]:
                lines.append(f"   {item['description']}")

        result_text = "\n".join(lines)
        logger.info(f"Returning {len(items)} news items ({len(result_text)} chars)")
        return {"success": True, "result": result_text}

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return {"success": False, "result": f"Gagal mengambil berita: {str(e)}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
