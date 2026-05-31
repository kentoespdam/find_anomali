# GitNexus Rules — Wajib Pakai Sebelum Edit Kode

Project ini di-index sebagai **find_anomali**. GitNexus = code intelligence
graph (symbols, calls, references, impact). **Default tool** untuk navigasi
kode di project ini.

## Kapan Wajib Pakai GitNexus

| Situasi                                  | Tool                                            |
| ---------------------------------------- | ----------------------------------------------- |
| Mau ubah function/class/method           | `gitnexus_impact({target, direction:"upstream"})` |
| Mau cari "dimana X dipakai / dipanggil"  | `gitnexus_query({query})`                       |
| Mau lihat definisi + tetangga sebuah simbol | `gitnexus_context({name})`                   |
| Mau rename simbol                        | `gitnexus_rename(...)`                          |
| Sebelum commit (verifikasi scope diff)   | `gitnexus_detect_changes()`                     |
| Mapping rute / API surface               | `gitnexus_route_map`, `gitnexus_tool_map`       |
| Cek shape data / kontrak antar modul     | `gitnexus_shape_check`                          |
| Query graph custom                       | `gitnexus_cypher({query})`                      |

**Dilarang** mengganti tool di atas dengan `grep -r` / `find` / scan rekursif —
itu hanya untuk fallback kalau GitNexus tidak punya jawabannya.

## Alur Wajib Sebelum Mengedit Simbol

1. `gitnexus_impact({ target: "<fqn>", direction: "upstream" })`.
2. Baca blast radius (callers, dependents). **Laporkan ke user** dalam 1–2 kalimat.
3. Kalau severity HIGH/CRITICAL → **warn user** dulu, tunggu konfirmasi.
4. Edit kode.
5. `gitnexus_detect_changes()` sebelum commit — pastikan scope sesuai.
6. Kalau index stale: `npx gitnexus analyze` lalu ulangi langkah 5.

## Skill Files (`.claude/skills/gitnexus/*/SKILL.md`)

| Task                              | Skill                       |
| --------------------------------- | --------------------------- |
| Arsitektur / "how does X work?"   | `gitnexus-exploring`        |
| Blast radius / safety analysis    | `gitnexus-impact-analysis`  |
| Debug error / trace bug           | `gitnexus-debugging`        |
| Refactor / rename / extract       | `gitnexus-refactoring`      |
| Tools & graph schema reference    | `gitnexus-guide`            |
| Index / status / wiki CLI         | `gitnexus-cli`              |
| Review PR / risk merge            | `gitnexus-pr-review`        |

Invoke via `Skill` tool saat task cocok dengan deskripsi di tabel.

## MCP Resources

Resource read-only via MCP:

```
gitnexus://repo/find_anomali/context
gitnexus://repo/find_anomali/clusters
gitnexus://repo/find_anomali/processes
gitnexus://repo/find_anomali/process/{name}
```

Pakai `ReadMcpResourceTool` untuk membaca isinya bila diperlukan ringkasan
struktural cepat.

## Reporting ke User

Setiap kali menjalankan `gitnexus_impact`, sampaikan ke user dengan format
ringkas:

```
Impact <target> (upstream):
- callers: N (severity: LOW|MEDIUM|HIGH|CRITICAL)
- key paths: a.py:42, b.py:integration_test
- risk note: <1 kalimat>
```

Kalau HIGH/CRITICAL: tahan edit, minta konfirmasi user dulu.

## Jangan Lupa

- Cek `gitnexus://repo/find_anomali/context` di awal sesi besar untuk
  orientasi cepat sebelum query lain.
- Update index setelah perubahan signifikan: `npx gitnexus analyze`.
- Kalau MCP tool belum ter-load (deferred), pakai `ToolSearch` query
  `select:mcp__gitnexus__impact,mcp__gitnexus__query,...` dulu.
