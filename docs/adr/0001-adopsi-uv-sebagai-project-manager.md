# Adopsi uv sebagai project manager

## Status

Accepted (2026-06-01)

## Konteks

Project baru, awalnya pakai `requirements.txt` unpinned + sistem Python. Tidak ada lockfile, tidak ada pinning interpreter, dependency resolution non-deterministik antar mesin. Sebelum kode produksi tumbuh, kita pindah ke tooling modern.

## Keputusan

Pakai **uv** (Astral) sebagai project manager penuh: dependency resolution + manajemen interpreter Python + lockfile + project metadata via `pyproject.toml` (PEP 621). Hapus `requirements.txt`.

Detail konfigurasi:

| Aspek | Pilihan | Alasan |
|---|---|---|
| Mode uv | Full (deps + interpreter + lock) | Manfaat penuh; `.python-version` ikut tracked |
| Python | 3.12 | Versi di mesin dev saat ini; cukup modern untuk semua deps |
| Layout | Package + flat (`anomali/` di root) | Tidak ada kebutuhan `src/`; struktur sudah ada |
| Build backend | Hatchling | Default uv `init --package`; minim konfigurasi |
| CLI entry | `find-anomali` → `anomali.cli:run` | Dash sesuai konvensi CLI nama; `_` tetap di package |
| Dev deps | PEP 735 `[dependency-groups] dev` | Standar baru; tidak install ke wheel publik (beda dengan `optional-dependencies`) |
| Pinning | Lower bounds + `uv.lock` | Manifest fleksibel, reproducibility via lockfile |
| Pytest config | `[tool.pytest.ini_options]` di `pyproject.toml` | Kurangi file root; satu tempat konfigurasi |
| Commit | `.python-version` + `uv.lock` | Reproduce antar mesin tanpa "works on my machine" |

## Alternatif yang dipertimbangkan

- **Tetap `requirements.txt`** — sederhana tapi tanpa lockfile, tanpa metadata, tanpa interpreter pinning. Cocok untuk script one-off, bukan project yang akan tumbuh.
- **Poetry / PDM** — kapabel, tapi lebih lambat, build backend & resolver terpisah, dan tidak manage interpreter sebaik uv.
- **pip-tools + venv manual** — workflow valid tapi banyak step manual; uv menggabungkan semuanya dalam satu binary cepat.
- **uv "tools only" mode** (cuma untuk install CLI global) — tidak menyelesaikan masalah project-level reproducibility.

## Konsekuensi

- **Onboarding berubah**: `pip install -r requirements.txt` → `uv sync`. Didokumentasikan di `CLAUDE.md`.
- **CI/CD nantinya** harus install uv dulu (bukan andalkan pip default). Saat ini belum ada CI; akan dialamatkan saat diset up.
- **Tooling MCP/agent** (Context7 rules, dll.) yang merujuk `requirements.txt` perlu diupdate. Sudah dilakukan di `docs/rules/02-context7.md`.
- **`uv.lock` di-commit** — review wajib mencakup perubahan lockfile (mirip `package-lock.json`).
- **`.python-version` di-commit** — pin interpreter ke 3.12; ubah hanya secara sadar.

## Referensi

- Beads issue: `find_anomali-coc`
- GitHub issue: kentoespdam/find_anomali#9
- Supersedes acceptance criteria di `find_anomali-f1t` (closed) yang menyebut `requirements.txt`
