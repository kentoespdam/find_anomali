# Project Instructions for AI Agents

**Source of truth produk:** [`PRD.md`](./PRD.md). Sebelum implementasi/perubahan logika deteksi, aturan, threshold, skema CSV, atau modul (`detector`, `config`, `db`, `exporter`, `cli`) — baca `PRD.md` dan jangan menyimpang darinya tanpa konfirmasi user.

## Pre-Coding Rules (WAJIB)

Baca sebelum menulis/mengedit kode. Urutannya mengikat.

1. [`docs/rules/00-pre-coding.md`](./docs/rules/00-pre-coding.md) — alur context check (PRD/ADR/issues) + checklist start sesi.
2. [`docs/rules/01-gitnexus.md`](./docs/rules/01-gitnexus.md) — wajib pakai GitNexus untuk navigasi & impact (bukan `grep`).
3. [`docs/rules/02-context7.md`](./docs/rules/02-context7.md) — wajib pakai Context7 untuk docs library/framework terbaru.

## Project Summary

CLI Python untuk deteksi anomali pemakaian air pra-cetak tagihan PDAM. Membaca table `rekairnow` dari MySQL, menerapkan aturan deteksi yang dikonfigurasi via `.env`, output CSV. Detail lengkap (problem, user stories, aturan, modul, threshold, testing) ada di `PRD.md`.

**Stack:** Python 3.12 (managed by uv), `mysql-connector-python`, `python-dotenv`, `pandas`, `pytest`. Build backend: `hatchling`. Dependency manifest: `pyproject.toml` (PEP 621 + PEP 735); lockfile `uv.lock`.

## Build & Test

Project ini pakai **uv** (Astral). Lihat ADR `docs/adr/0001-adopsi-uv-sebagai-project-manager.md`.

```bash
uv sync                       # install runtime + dev deps dari uv.lock
uv run pytest                 # jalankan test
uv run find-anomali           # jalankan CLI (entry point: anomali.cli:run)
```

**Manajemen dependensi:**
```bash
uv add <pkg>                  # tambah runtime dep
uv add --dev <pkg>            # tambah dev dep ke [dependency-groups] dev
uv remove <pkg>               # hapus dep
uv lock --upgrade             # refresh lockfile (resolve ulang)
uv lock --upgrade-package <pkg>  # refresh satu package saja
```

`uv.lock` dan `.python-version` di-commit. Jangan edit `uv.lock` manual.

## Beads Issue Tracker

Project ini pakai **bd (beads)**. Jalankan `bd prime` untuk command reference lengkap.

```bash
bd ready                    # cari work yang siap
bd show <id>                # detail issue
bd update <id> --claim      # claim work
bd close <id>               # tutup
bd remember "insight"       # simpan knowledge lintas sesi (jangan pakai MEMORY.md)
```

**Aturan:**
- Pakai `bd` untuk SEMUA task tracking — jangan TodoWrite/TaskCreate/markdown TODO.
- Pakai `bd remember`, bukan `MEMORY.md`.
- Buat issue **sebelum** menulis kode; tandai `in_progress` saat mulai.

## Non-Interactive Shell

Aliases sistem bisa memaksa `-i` (prompt y/n) → agent hang. Selalu pakai flag non-interaktif:

```bash
cp -f / mv -f / rm -f       # NOT cp/mv/rm tanpa flag
rm -rf dir                  # NOT rm -r
apt-get -y …                # auto-yes
ssh -o BatchMode=yes …      # fail, jangan prompt
```

## Session Completion

Sebelum bilang "done", jalankan checklist berikut. Kerja BELUM selesai sampai `git push` sukses.

1. **File follow-up issues** untuk sisa kerja.
2. **Quality gates** (jika kode berubah): `pytest`, linter, build.
3. **Update issue status:** `bd close <id1> <id2> …`.
4. **Push:**
   ```bash
   git pull --rebase
   bd dolt push
   git push
   git status                # harus "up to date with origin"
   ```
5. **Clean up:** clear stashes, prune remote branches.
6. **Verify & hand off.**

**JANGAN** stop sebelum push, jangan bilang "ready to push when you are" — push sendiri. Kalau push gagal, resolve dan retry.

## GitNexus — Code Intelligence

Project ini di-index sebagai **find_anomali**. Pakai MCP tools GitNexus untuk navigasi & impact analysis.

**gitnexus repo** : `gitnexus://repo/find_anomali`.

**Wajib:**
- Sebelum mengedit symbol (function/class/method): `gitnexus_impact({target, direction: "upstream"})`. Laporkan blast radius ke user. Warn jika HIGH/CRITICAL.
- Sebelum commit: `gitnexus_detect_changes()` untuk verifikasi scope.
- Eksplorasi: `gitnexus_query({query})` dan `gitnexus_context({name})` — bukan grep.
- Rename: `gitnexus_rename` — bukan find-and-replace.

Jika tool warn stale: `npx gitnexus analyze`.

**Resources:** `gitnexus://repo/find_anomali/{context,clusters,processes,process/{name}}`.

**Skill files** (`.claude/skills/gitnexus/*/SKILL.md`):

| Task | Skill |
|------|-------|
| Arsitektur / "how does X work?" | `gitnexus-exploring` |
| Blast radius | `gitnexus-impact-analysis` |
| Debug | `gitnexus-debugging` |
| Refactor / rename / extract | `gitnexus-refactoring` |
| Tools & schema reference | `gitnexus-guide` |
| Index/status/wiki CLI | `gitnexus-cli` |

## Conventions

- Logika deteksi (`detector`) **harus** murni — tanpa I/O DB/filesystem — sesuai keputusan di `PRD.md` agar dapat di-unit-test tanpa MySQL.
- Threshold tidak di-hardcode di luar default config; semua tunable lewat `.env`. Lihat `PRD.md` untuk daftar key & default.
- Satu baris bisa dapat banyak kategori anomali (separator `;` untuk kategori, ` | ` untuk keterangan).
