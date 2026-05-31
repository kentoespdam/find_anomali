# PRD — Deteksi Anomali Pemakaian Air Pra-Cetak Tagihan

> Beads issue: `find_anomali-qb1` · feature · P1 · `needs-triage`

## Problem Statement

Sebagai petugas billing PDAM, setiap akhir periode pencatatan meter saya menerima ribuan baris pemakaian air di table `rekairnow` yang akan langsung dijadikan tagihan. Sebagian baris mengandung kesalahan input meter (petugas salah baca, ketukar `met_l`/`met_k`, lompat digit, lupa baca, dsb). Kalau tagihan keburu tercetak dengan data salah, pelanggan komplain, kantor harus revisi tagihan, dan kepercayaan turun. Saat ini tidak ada laporan otomatis yang menandai baris-baris yang patut dicurigai sebelum proses cetak.

## Solution

Sebuah skrip Python CLI yang menarik seluruh isi table `rekairnow`, menerapkan sekumpulan aturan deteksi anomali yang dapat dikonfigurasi via `.env`, dan menghasilkan file CSV berisi baris-baris yang perlu di-review beserta kategori anomalinya. Petugas membuka CSV di Excel, mengoreksi baris yang memang salah, lalu menjalankan proses cetak tagihan.

Aturan deteksi mencakup anomali fisik (meter mundur, mismatch kalkulasi, mismatch nol), anomali pola (pemakaian jauh di atas/di bawah rata-rata 3 bulan terakhir dengan minimum selisih absolut), serta kasus khusus (pelanggan tanpa baseline, data NULL). Semua threshold dapat di-tune dari `.env` tanpa mengubah kode.

## User Stories

1. As a petugas billing, I want melihat daftar nosamw dengan pemakaian jauh di atas rata-rata, so that saya bisa konfirmasi ke petugas baca meter sebelum tagihan tercetak.
2. As a petugas billing, I want melihat daftar nosamw dengan pemakaian jauh di bawah rata-rata, so that saya bisa cek apakah meter dicatat tidak penuh atau ada kesalahan tukar `met_l`/`met_k`.
3. As a petugas billing, I want baris dengan `met_k < met_l` di-flag, so that saya bisa cek apakah benar ada penggantian meter atau ini salah input.
4. As a petugas billing, I want baris dengan `pakai ≠ (met_k - met_l)` di-flag, so that saya tahu ada inkonsistensi antara nilai meter dan nilai pakai yang akan ditagih.
5. As a petugas billing, I want baris dengan `pakai = 0` padahal `met_k > met_l` (atau sebaliknya) di-flag, so that saya tahu pencatatan tidak konsisten.
6. As a petugas billing, I want baris dengan `rata2 = 0` (pelanggan baru / habis pasang ulang) tidak ke-flag setiap saat hanya karena rasio meledak, so that laporan tidak penuh false-positive untuk pelanggan baru.
7. As a petugas billing, I want pelanggan tanpa baseline tetap di-flag jika pemakaian melebihi batas wajar absolut, so that saya tetap bisa menangkap pemakaian ekstrim di pelanggan baru.
8. As a petugas billing, I want baris dengan kolom `met_l`/`met_k`/`pakai`/`rata2` bernilai NULL di-flag terpisah, so that saya tahu data ini belum siap untuk ditagih.
9. As a petugas billing, I want pelanggan dengan pemakaian kecil tidak ke-flag walau rasionya tinggi (mis. rata2=2, pakai=7), so that saya tidak buang waktu mengecek anomali yang dampak rupiahnya minim.
10. As a petugas billing, I want satu baris dapat di-flag oleh lebih dari satu kategori sekaligus, so that saya tahu semua alasan kecurigaan sebuah baris dalam satu pandangan.
11. As a petugas billing, I want output dalam format CSV, so that saya bisa membukanya di Excel, sort, filter, dan tandai baris yang sudah dicek.
12. As a petugas billing, I want CSV berisi `nosamw`, `met_l`, `met_k`, `pakai`, `rata2`, `selisih_meter`, `selisih_vs_rata2`, `rasio`, `kategori_anomali`, dan `keterangan`, so that saya tidak perlu bolak-balik ke sistem utama untuk konteks dasar.
13. As a petugas billing, I want keterangan ditulis dalam bahasa yang menjelaskan kenapa baris itu ke-flag (mis. `pakai=120 > 3x rata2=30`), so that saya bisa langsung paham tanpa membaca dokumentasi aturan.
14. As a kepala bagian billing, I want bisa mengubah threshold rasio dan minimum selisih tanpa minta developer, so that aturan bisa di-tune mengikuti karakter wilayah layanan.
15. As a admin sistem, I want kredensial database dan threshold disimpan di `.env`, so that tidak ada kredensial yang ke-commit ke repo dan konfigurasi mudah dibedakan per environment.
16. As a admin sistem, I want tersedia `.env.example` sebagai template, so that orang baru tahu env var apa saja yang perlu di-set.
17. As a admin sistem, I want skrip dijalankan dari satu baris perintah, so that bisa dijadwalkan via cron sebelum proses cetak rutin.
18. As a admin sistem, I want skrip menampilkan ringkasan jumlah baris diperiksa dan jumlah anomali, so that saya tahu skrip jalan sehat tanpa membuka CSV-nya.
19. As a developer, I want logika deteksi terpisah dari I/O database dan I/O file, so that logika bisa di-unit-test tanpa MySQL atau filesystem.
20. As a developer, I want unit test mencakup seluruh kategori anomali termasuk edge case (`rata2=0`, NULL, pelanggan kecil), so that perubahan threshold di masa depan tidak diam-diam memecahkan aturan lain.

## Implementation Decisions

**Stack & runtime**
- Python 3 CLI script, dijalankan dari terminal.
- Dependencies: `mysql-connector-python` (driver), `python-dotenv` (load `.env`), `pandas` (manipulasi data dan export CSV).
- Konfigurasi dibaca dari `.env` di working directory; `.env.example` di-commit sebagai template; `.env` di-gitignore.

**Modul**
- **`detector`** (deep module, pure logic) — input: satu record (atau iterable record) berisi `met_l`, `met_k`, `pakai`, `rata2` plus objek threshold. Output: daftar kategori anomali + keterangan human-readable. Tidak menyentuh DB, tidak menyentuh filesystem. Inilah modul utama yang ditest.
- **`config`** — baca `.env`, validasi tipe (float/int), sediakan default kalau key absen, ekspos sebagai objek/typed dict.
- **`db`** — buka koneksi MySQL, eksekusi `SELECT nosamw, met_l, met_k, pakai, rata2 FROM <DB_TABLE>`, kembalikan DataFrame. Nama table dari `.env` (`DB_TABLE`, default `rekairnow`).
- **`exporter`** — terima DataFrame anomali, tulis ke path CSV dari `.env`.
- **`cli`** — wiring: config → db → detector → exporter → ringkasan ke stdout.

**Aturan deteksi (final)**

| Kategori | Kondisi |
|---|---|
| `DATA_NULL` | Salah satu dari `met_l`/`met_k`/`pakai`/`rata2` bernilai NULL. Cek lain di-skip untuk baris ini. |
| `METER_MUNDUR` | `met_k < met_l` |
| `MISMATCH_PAKAI` | `pakai ≠ (met_k − met_l)` |
| `MISMATCH_NOL` | `pakai = 0` dan `met_k > met_l`, atau `pakai > 0` dan `met_k = met_l` |
| `TANPA_BASELINE` | `rata2 = 0` dan `pakai > TANPA_BASELINE_MAX` |
| `PEMAKAIAN_TINGGI` | `rata2 > 0` dan `pakai > RATIO_TINGGI × rata2` dan `(pakai − rata2) > MIN_SELISIH` |
| `PEMAKAIAN_RENDAH` | `rata2 > 0` dan `pakai < rata2 / RATIO_RENDAH` dan `(rata2 − pakai) > MIN_SELISIH` |

Satu baris dapat memperoleh banyak kategori. Output kategori dirangkai dengan separator `;`; keterangan dirangkai dengan separator ` | `.

**Konfigurasi via `.env`**

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_TABLE` (default `rekairnow`).
- `RATIO_TINGGI` (default `3.0`).
- `RATIO_RENDAH` (default `3.0`).
- `MIN_SELISIH` (default `10`).
- `TANPA_BASELINE_MAX` (default `30`).
- `OUTPUT_PATH` (default `anomali.csv`).

Semua threshold opsional; default ada di kode.

**Kolom output CSV**
`nosamw, met_l, met_k, pakai, rata2, selisih_meter, selisih_vs_rata2, rasio, kategori_anomali, keterangan`. `rasio` dibiarkan kosong untuk baris dengan `rata2 = 0` atau NULL.

**Arsitektur eksekusi**
Logika dijalankan di Python (pandas), seluruh isi table ditarik sekaligus. Asumsi volume < 500rb baris. Bila kelak ternyata melampaui, struktur sudah memisahkan `db` dari `detector` sehingga pre-filter SQL bisa ditambahkan tanpa mengubah modul logic.

## Testing Decisions

**Filosofi tes**
Tes hanya mengevaluasi perilaku eksternal modul `detector`: untuk input record tertentu, apakah daftar kategori dan keterangan yang dikeluarkan benar. Tidak ada tes terhadap struktur internal, urutan iterasi, atau implementation detail seperti nama fungsi helper.

**Modul yang di-test**
Hanya `detector`. Modul I/O (`db`, `exporter`) tipis dan tidak perlu tes — bila berubah, manfaat tes lebih kecil daripada biaya maintenance-nya. `cli` cuma wiring.

**Kasus tes yang harus tercakup**
- Baris normal (tidak ke-flag).
- `METER_MUNDUR` murni.
- `MISMATCH_PAKAI` murni.
- `MISMATCH_NOL` dua arah.
- `TANPA_BASELINE` di atas dan di bawah `TANPA_BASELINE_MAX`.
- `PEMAKAIAN_TINGGI` melewati rasio tetapi gagal `MIN_SELISIH` (pelanggan kecil).
- `PEMAKAIAN_TINGGI` melewati kedua syarat.
- `PEMAKAIAN_RENDAH` simetris (kedua kasus).
- `DATA_NULL` pada masing-masing kolom; harus skip cek lain.
- Baris yang ke-flag oleh banyak kategori sekaligus (mis. `METER_MUNDUR` + `MISMATCH_PAKAI`).
- Threshold custom (override default) membuktikan logika membaca threshold yang di-pass-in.

**Prior art**
Belum ada — project baru. Tes ditulis dengan `pytest` (lintang industri Python paling umum), satu file `tests/test_detector.py`, satu test function per kasus dengan parametrize untuk variasi nilai.

## Out of Scope

- Deteksi kebocoran pipa pelanggan (perlu tren multi-bulan, butuh history table).
- Deteksi pencurian air / meter macet (perlu pola flat antar bulan, butuh history).
- Anomali absolut sebagai kategori sendiri (mis. `pakai > 1000 m³`) — di-skip karena threshold absolut sulit dipilih tanpa data profil pelanggan; bisa ditambahkan belakangan.
- Integrasi langsung ke sistem cetak tagihan; output berhenti di file CSV.
- JOIN ke table master pelanggan (nama, alamat, golongan tarif) — bisa ditambahkan kalau dibutuhkan, tapi tidak di MVP.
- Web dashboard interaktif (sort/filter/tandai-sudah-dicek).
- Penjadwalan otomatis; diserahkan ke `cron` di luar skrip.
- Notifikasi (email/WhatsApp) hasil deteksi.

## Further Notes

- Tipe data `met_l`/`met_k`/`pakai`/`rata2` perlu dikonfirmasi saat implementasi: bila `DECIMAL`, perbandingan `pakai != met_k - met_l` perlu toleransi numerik (±0.001) untuk menghindari false-positive akibat presisi.
- `pd.read_sql` akan memunculkan warning bila bukan SQLAlchemy connection; bisa diganti pakai cursor manual + konstruktor DataFrame bila warning mengganggu.
- Loop per-baris di `detector` dipilih demi keterbacaan; bisa di-vectorize bila volume membesar tanpa mengubah interface publik.
- Skrip aman jalan berulang kali (read-only terhadap DB); hanya menulis CSV di working directory.
