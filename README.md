# 📰 XiaoZhi News MCP Server
Berita terbaru dari **Kompas.com** & **Antara News** untuk XiaoZhi ESP32.

---

## 🚀 Setup (4 Langkah)

### 1. Pastikan Python 3.7+ terinstall
```bash
python --version
```

### 2. Download file ini, lalu install dependency
```bash
pip install -r requirements.txt
```

### 3. Buat file `.env` dan isi token kamu
```bash
cp .env.example .env
```
Edit file `.env`, ganti `GANTI_DENGAN_TOKEN_BARU_KAMU` dengan token WSS kamu dari konsol xiaozhi.me.

> ⚠️ Token WSS kamu sudah terekspos di chat. Segera **regenerate** di xiaozhi.me sebelum dipakai!

### 4. Jalankan!
```bash
# Download mcp_pipe.py dari repo resmi XiaoZhi:
# https://github.com/78/mcp-calculator/blob/main/mcp_pipe.py
# Letakkan di folder yang sama, lalu:

python mcp_pipe.py news_server.py
```

---

## Output yang diharapkan
```
2025-xx-xx - MCP_PIPE - INFO - Connecting to WebSocket server...
2025-xx-xx - MCP_PIPE - INFO - Successfully connected to WebSocket server
2025-xx-xx - MCP_PIPE - INFO - Started news_server.py process
Processing request of type ListToolsRequest
Processing request of type CallToolRequest
```

---

## 🗣️ Cara Tanya ke XiaoZhi
Setelah server berjalan, langsung tanya ke perangkat ESP32:

- *"Ada berita apa hari ini?"*
- *"Berita nasional terbaru?"*
- *"Kabar teknologi terkini?"*
- *"Ceritakan berita olahraga hari ini"*
- *"Berita internasional terbaru?"*
- *"Berita bisnis hari ini?"*

---

## 📡 Kategori Berita

| Kata kunci       | Sumber               |
|------------------|----------------------|
| `nasional`       | Kompas Nasional      |
| `internasional`  | Kompas Internasional |
| `bisnis`         | Kompas Bisnis        |
| `teknologi`      | Kompas Tekno         |
| `olahraga`       | Kompas Olahraga      |
| `terkini`        | Antara News          |

---

## 📁 Struktur File
```
xiaozhi-news/
├── news_server.py    ← MCP tool berita (file utama)
├── mcp_pipe.py       ← Download dari github.com/78/mcp-calculator
├── mcp_config.json   ← Konfigurasi server
├── requirements.txt  ← Python dependencies
├── .env              ← Token WSS kamu (JANGAN di-commit ke Git!)
└── .env.example      ← Template .env
```
