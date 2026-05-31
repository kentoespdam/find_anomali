# Context7 Rules — Wajib Pakai untuk Docs Library

Context7 = MCP server yang mengambil **dokumentasi terbaru** library /
framework / SDK / CLI / cloud service. Pengetahuan internal model bisa basi
(cutoff training), jadi setiap kali agent menyentuh API eksternal **wajib**
verifikasi lewat Context7 sebelum menulis kode.

## Kapan WAJIB Pakai Context7

- Setup / install library baru (mis. `uv add <pkg>` ke `pyproject.toml`).
- Pakai API library yang sudah ada (`pandas`, `mysql-connector-python`,
  `python-dotenv`, `pytest`, dll.) — terutama signature fungsi, parameter,
  default value, exception, atau best-practice idiom.
- Migrasi versi library (mis. pandas 1.x → 2.x).
- Pakai CLI tool / cloud service (Cloudflare, AWS, dll.) — flag & format config.
- Debug bug yang **spesifik ke library** (bukan business logic kita).

## Kapan SKIP Context7

- Refactor murni internal (tidak menyentuh API eksternal).
- Bug di business logic / aturan deteksi kita sendiri.
- Code review struktural.
- Konsep umum non-library (algoritma, design pattern generik).

## Alur Pakai Context7

1. `mcp__context7__resolve-library-id({ libraryName, fullQuestion })`.
   - Skip langkah ini kalau user sudah kasih ID `/org/project` eksplisit.
2. Pilih match terbaik berdasarkan: nama persis, relevansi, snippet count,
   reputasi (High/Medium), score. Cocokkan versi kalau user spesifik.
3. `mcp__context7__query-docs({ libraryId, fullQuestion })`.
4. **Jawab strict berdasarkan docs yang diambil** — jangan campur dengan
   tebakan dari training data.

Kalau hasil resolve jelek (irrelevant), coba nama alternatif sebelum menyerah.

## Prioritas

- **Context7 > Web Search** untuk library docs. Jangan langsung WebSearch
  kecuali Context7 tidak punya library tersebut.
- Untuk Anthropic / Claude API → ada skill khusus `claude-api`; pakai itu.
- Untuk Cloudflare → ada skill `cloudflare:*`; pakai itu.

## Contoh Pemicu (Trigger Phrases)

User bilang… → pakai Context7:
- "Pakai pandas untuk grouping…"
- "Connect ke MySQL pakai mysql-connector"
- "Load .env via python-dotenv"
- "Setup pytest fixture untuk…"
- "Cara baca CSV streaming di pandas 2.x"

## Reporting ke User

Kalau jawaban berasal dari Context7, sebut sumbernya singkat di response:

```
(Source: Context7 — /pandas-dev/pandas, query: "read_csv chunksize")
```

Supaya user tahu dasar saran kita up-to-date, bukan tebakan.

## Catatan Teknis

- Tool Context7 mungkin deferred. Load via:
  `ToolSearch({ query: "select:mcp__context7__resolve-library-id,mcp__context7__query-docs" })`.
- Cache jawaban Context7 untuk pertanyaan berulang dalam sesi yang sama — jangan
  spam query identik.
