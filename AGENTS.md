# Agent Instructions

Semua aturan agent (beads workflow, session completion, GitNexus, shell non-interaktif, conventions) ada di **[`CLAUDE.md`](./CLAUDE.md)** — itu sumber utama.

Spesifikasi produk (problem, user stories, aturan deteksi, modul, threshold, testing) ada di **[`PRD.md`](./PRD.md)** — itu source of truth aplikasi.

**Pre-Coding Rules (WAJIB)** — baca dulu sebelum menulis kode:
- [`docs/rules/00-pre-coding.md`](./docs/rules/00-pre-coding.md) — alur context check (PRD/ADR/issues) + checklist start sesi.
- [`docs/rules/01-gitnexus.md`](./docs/rules/01-gitnexus.md) — wajib pakai GitNexus untuk navigasi & impact.
- [`docs/rules/02-context7.md`](./docs/rules/02-context7.md) — wajib pakai Context7 untuk docs library/framework terbaru.

Baca semuanya sebelum bekerja. Jangan duplikasi isinya di file lain.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **find_anomali** (142 symbols, 178 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/find_anomali/context` | Codebase overview, check index freshness |
| `gitnexus://repo/find_anomali/clusters` | All functional areas |
| `gitnexus://repo/find_anomali/processes` | All execution flows |
| `gitnexus://repo/find_anomali/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
