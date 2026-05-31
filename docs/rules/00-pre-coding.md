# Pre-Coding Rules (WAJIB dibaca sebelum menulis kode)

Aturan ini **mengikat** untuk setiap sesi agent. Pelanggaran = stop dan baca ulang.

## 1. Pahami Context Dulu — Jangan Langsung Coding

Sebelum menulis/mengedit satu baris kode pun, agent **HARUS** menyelesaikan urutan ini:

1. **Baca `PRD.md`** — source of truth produk (aturan deteksi, threshold, modul,
   skema CSV). Jangan menyimpang tanpa konfirmasi user.
2. **Baca ADR** di `docs/adr/` (jika ada) — keputusan arsitektur yang mengikat.
   Jika tidak ada folder, anggap kosong; jangan buat ADR baru kecuali diminta.
3. **Cek `issues` di beads:**
   - `bd ready` — issue yang siap dikerjakan.
   - `bd list --status=in_progress` — yang sedang berjalan.
   - `bd show <id>` — detail issue terkait sebelum claim.
   - Cari isu terkait dengan `bd search <keyword>` sebelum membuat duplikat.
4. **Recall memory lintas sesi:** `bd memories <keyword>` untuk insight yang sudah disimpan.
5. **Buat / claim issue dulu** baru tulis kode. Tandai `in_progress` saat mulai.

Jika ada konflik antara PRD, ADR, dan issue → **berhenti** dan tanya user. Jangan
asumsikan.

## 2. Wajib Pakai GitNexus untuk Navigasi & Impact

Project ini di-index sebagai **find_anomali**. **Dilarang** pakai `grep`/`find`
sebagai cara utama mengeksplorasi simbol — gunakan GitNexus dulu. Lihat
[`01-gitnexus.md`](./01-gitnexus.md) untuk daftar tool & alur lengkap.

Aturan inti:
- Sebelum **mengedit symbol** apa pun (function/class/method):
  `gitnexus_impact({ target, direction: "upstream" })`. Laporkan blast radius
  ke user dan **warn** kalau HIGH/CRITICAL sebelum lanjut.
- Sebelum **commit**: `gitnexus_detect_changes()` untuk verifikasi scope.
- Eksplorasi arsitektur: `gitnexus_query` + `gitnexus_context`, bukan grep.
- Rename simbol: `gitnexus_rename` — **bukan** find-and-replace manual.
- Jika tool warn index stale → `npx gitnexus analyze` sebelum lanjut.

Detail tool, skill files, dan resource MCP ada di [`01-gitnexus.md`](./01-gitnexus.md).

## 3. Wajib Pakai Context7 untuk Docs Library/Framework

Setiap kali menyentuh API library/framework/CLI/cloud service (mis. `pandas`,
`mysql-connector-python`, `pytest`, `python-dotenv`, dst.) — **wajib** ambil
dokumentasi terbaru lewat Context7 sebelum menulis kode yang memakai API
tersebut. Pengetahuan internal model bisa basi.

Aturan inti:
- Jangan menebak signature/flag/opsi API. Ambil dari Context7.
- Hindari Web Search untuk dokumentasi library — Context7 didahulukan.
- Skip Context7 hanya untuk: refactor murni, business logic bug, code review,
  konsep umum non-library.

Alur dan contoh ada di [`02-context7.md`](./02-context7.md).

## 4. Etika Coding & Sesi

- Logika `detector` **harus murni** (tanpa I/O DB/FS) sesuai PRD.
- Threshold lewat `.env` saja — jangan hardcode di luar default config.
- Satu baris bisa banyak kategori anomali: separator `;` (kategori) dan ` | `
  (keterangan).
- Pakai `bd` untuk semua task tracking — **jangan** TodoWrite/TaskCreate/markdown TODO.
- Shell non-interaktif: `cp -f`, `rm -rf`, `apt-get -y`, dll.
- Sesi belum selesai sampai `pytest` hijau, issue di-close (`bd close <id>`),
  dan `git push` sukses. Lihat “Session Completion” di [`CLAUDE.md`](../../CLAUDE.md).

## 5. Checklist Sebelum Mulai (copy-paste ke chat saat mulai sesi)

```
[ ] Sudah baca PRD.md bagian yang relevan
[ ] Sudah cek docs/adr/ (jika ada)
[ ] Sudah jalankan: bd ready / bd show <id> / bd search <keyword>
[ ] Sudah klaim issue (bd update <id> --claim) atau buat baru
[ ] Sudah jalankan gitnexus_impact untuk simbol yang akan diedit
[ ] Sudah ambil docs library via Context7 (jika menyentuh API eksternal)
```

Belum semua tercentang? **Jangan menulis kode.**
