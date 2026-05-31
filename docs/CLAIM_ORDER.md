# Claim Order — find_anomali

Urutan claim issue `bd` untuk MVP deteksi anomali `rekairnow`. Ikuti urutan dari atas ke bawah; setiap slice memblokir slice berikutnya (kecuali yang ditandai paralel).

## Quick reference

```bash
bd ready                       # cek apa yang siap di-claim
bd show <id>                   # detail issue
bd update <id> --claim         # mulai
bd close <id>                  # selesai
```

Parent epic: `find_anomali-qb1` (jangan di-claim; akan tertutup setelah semua anak selesai).

---

## Order

### 1. `find_anomali-f1t` — Tracer bullet: scaffolding + METER_MUNDUR

**Type:** AFK · **Blocks:** 4 slice berikutnya · **Status:** ready

- [ ] `bd update find_anomali-f1t --claim`
- [ ] `requirements.txt` berisi `mysql-connector-python`, `python-dotenv`, `pandas`, `pytest`
- [ ] `.env.example` berisi `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_TABLE` (default `rekairnow`), `OUTPUT_PATH` (default `anomali.csv`)
- [ ] `.env` di-gitignore
- [ ] `config` module: load `.env`, expose typed config dengan default
- [ ] `db` module: koneksi MySQL, return DataFrame `SELECT nosamw, met_l, met_k, pakai, rata2 FROM <DB_TABLE>`
- [ ] `detector` module: pure (no I/O), input record + threshold → list kategori + keterangan
- [ ] `detector` implementasi rule `METER_MUNDUR` saja
- [ ] `exporter` tulis CSV dengan skema penuh: `nosamw, met_l, met_k, pakai, rata2, selisih_meter, selisih_vs_rata2, rasio, kategori_anomali, keterangan`
- [ ] `python -m anomali` jalan end-to-end (config → db → detector → exporter)
- [ ] `tests/test_detector.py`: positive `METER_MUNDUR` + negative normal-row, pytest hijau
- [ ] `bd close find_anomali-f1t`

---

### 2. Slice paralel (semua unblock setelah `f1t` close)

Setelah `f1t` selesai, empat slice berikut bisa di-claim dalam urutan apa pun. Rekomendasi: kerjakan satu per satu, **`1db` dulu** karena `qrk` (HITL) bergantung padanya.

#### 2a. `find_anomali-1db` — detector: MISMATCH_PAKAI + MISMATCH_NOL + multi-category aggregation

**Type:** AFK · **Blocks:** `qrk`

- [ ] `bd update find_anomali-1db --claim`
- [ ] `detector` implementasi `MISMATCH_PAKAI` (`pakai != met_k - met_l`)
- [ ] `detector` implementasi `MISMATCH_NOL` dua arah
- [ ] Multi-category: kategori join `;`, keterangan join ` | `
- [ ] Keterangan berisi nilai yang men-trigger (mis. `pakai=5 tapi met_k-met_l=8`)
- [ ] CSV multi-category baris tampil benar
- [ ] Tests: pure `MISMATCH_PAKAI`, pure `MISMATCH_NOL` dua arah, `METER_MUNDUR` + `MISMATCH_PAKAI` bareng
- [ ] `bd close find_anomali-1db`

#### 2b. `find_anomali-7t9` — detector: DATA_NULL skip-other-checks

**Type:** AFK

- [ ] `bd update find_anomali-7t9 --claim`
- [ ] `detector` flag `DATA_NULL` jika salah satu `met_l`/`met_k`/`pakai`/`rata2` NULL
- [ ] Saat `DATA_NULL` aktif, tidak ada kategori lain ditambahkan
- [ ] Keterangan sebut kolom mana yang NULL
- [ ] CSV `rasio` kosong untuk baris NULL
- [ ] Tests: tiap kolom NULL individual trigger `DATA_NULL` dan TIDAK trigger `METER_MUNDUR` walau `met_k < met_l`
- [ ] `bd close find_anomali-7t9`

#### 2c. `find_anomali-ojn` — detector: PEMAKAIAN_TINGGI + PEMAKAIAN_RENDAH

**Type:** AFK · **Blocks:** `egt`

- [ ] `bd update find_anomali-ojn --claim`
- [ ] `config` baca `RATIO_TINGGI` (3.0), `RATIO_RENDAH` (3.0), `MIN_SELISIH` (10) dari `.env`
- [ ] `.env.example` di-update
- [ ] `PEMAKAIAN_TINGGI`: `rata2 > 0` AND `pakai > RATIO_TINGGI * rata2` AND `(pakai - rata2) > MIN_SELISIH`
- [ ] `PEMAKAIAN_RENDAH`: `rata2 > 0` AND `pakai < rata2 / RATIO_RENDAH` AND `(rata2 - pakai) > MIN_SELISIH`
- [ ] Guard `rata2 > 0` (no division by zero)
- [ ] CSV `rasio` dan `selisih_vs_rata2` terisi
- [ ] Keterangan sebut nilai trigger (mis. `pakai=120 > 3x rata2=30`)
- [ ] Tests: ratio lewat tapi `MIN_SELISIH` gagal (pelanggan kecil → tidak flag), dua syarat lewat → flag, simetris low, custom threshold override
- [ ] `bd close find_anomali-ojn`

#### 2d. `find_anomali-3zu` — cli: stdout summary

**Type:** AFK

- [ ] `bd update find_anomali-3zu --claim`
- [ ] CLI print total baris source
- [ ] CLI print total baris anomali
- [ ] CLI print per-kategori breakdown
- [ ] Output ke stdout (bukan stderr), aman untuk redirect `cron`
- [ ] Exit code 0 selalu (sukses, terlepas dari ada anomali atau tidak)
- [ ] `bd close find_anomali-3zu`

---

### 3. `find_anomali-egt` — detector: TANPA_BASELINE

**Type:** AFK · **Blocked by:** `ojn`

- [ ] `bd update find_anomali-egt --claim`
- [ ] `config` baca `TANPA_BASELINE_MAX` (default 30)
- [ ] `.env.example` di-update
- [ ] `detector` flag `TANPA_BASELINE` jika `rata2 = 0` AND `pakai > TANPA_BASELINE_MAX`
- [ ] Baris `rata2 = 0` tidak pernah dapat `PEMAKAIAN_TINGGI`/`PEMAKAIAN_RENDAH`
- [ ] CSV `rasio` kosong untuk baris `rata2 = 0`
- [ ] Tests: `rata2=0` & `pakai > max` (flag), `rata2=0` & `pakai <= max` (tidak flag), `rata2=0` tidak trigger high/low
- [ ] `bd close find_anomali-egt`

---

### 4. `find_anomali-qrk` — HITL: DECIMAL tolerance untuk MISMATCH_PAKAI

**Type:** HITL · **Blocked by:** `1db` · **Label:** `human-needed`

- [ ] `bd update find_anomali-qrk --claim`
- [ ] **[HITL]** Bersama user: jalankan `DESCRIBE rekairnow`, konfirmasi tipe `met_l`, `met_k`, `pakai`, `rata2`
- [ ] Dokumentasikan tipe di notes issue
- [ ] Cabang DECIMAL: `MISMATCH_PAKAI` pakai toleransi ±0.001, tambahkan test boundary (just inside / just outside)
- [ ] Cabang integer: dokumentasikan, no code change
- [ ] `bd close find_anomali-qrk`

---

## Session close

Setelah semua slice tertutup:

```bash
git status
git add .
git commit -m "..."
bd dolt push
git push
git status   # harus "up to date with origin"
```
