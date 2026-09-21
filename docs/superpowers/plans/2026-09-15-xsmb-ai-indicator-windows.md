# XSMB AI Indicator Windows Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a self-contained 64-bit Windows desktop `XSMB_AI_Indicator.exe` that updates XSMB history, ranks 00–99, displays statistical indicators, and performs leak-free walk-forward backtesting.

**Architecture:** Replace the V1 Flask/browser launcher with a native Tkinter desktop shell. Keep network retrieval, parsing, SQLite persistence, analytics, backtest, and UI as isolated modules; package the entry point with PyInstaller while storing user data under `%LOCALAPPDATA%/XSMB_AI_Indicator`.

**Tech Stack:** Python 3.11+, standard-library Tkinter/ttk, SQLite3, urllib, pytest, PyInstaller.

**Spec:** `docs/superpowers/specs/2026-09-15-xsmb-ai-indicator-windows-design.md`

## Global Constraints
- Normal use must not require Python, pip, Flask, a `.bat` file, a browser, or localhost.
- `AI Score` is labeled as a statistical ranking score, not a true winning probability.
- Malformed source pages must never be persisted as valid draws.
- User history must survive replacement of the EXE.
- Network work must not block the desktop UI.
- Release requires all automated tests to pass.

---

### Task 1: Domain parser and validated draw model
**Files:** Create `src/models.py`, `src/parser.py`, `tests/fixtures/sample_draw.html`, `tests/test_parser.py`.

**Interfaces:** `parse_draw(html: str, source_url: str) -> Draw`; `Draw(day: str, numbers: tuple[str,...], special_prize: str, source_url: str)`.

- [ ] Write tests proving a known fixture yields exactly 27 two-digit values and malformed HTML raises `ParseError`.
- [ ] Run `pytest tests/test_parser.py -v` and confirm RED because parser/model do not exist.
- [ ] Implement `Draw`, `ParseError`, structural prize parsing and validation.
- [ ] Run parser tests and confirm GREEN.
- [ ] Commit `feat: add validated XSMB parser`.

### Task 2: Persistent SQLite repository
**Files:** Create `src/storage.py`, `tests/test_storage.py`.

**Interfaces:** `Repository(db_path)`, `save_draw(draw)`, `list_draws()`, `save_prediction(target_day, ranking)`, `list_predictions()`.

- [ ] Write tests using a temporary DB proving schema creation, draw round-trip, prediction persistence and replacement without duplicate dates.
- [ ] Run storage tests and confirm RED.
- [ ] Implement schema for `draws`, `predictions`, `settings`, including source URL and fetched timestamp.
- [ ] Run storage tests and confirm GREEN.
- [ ] Commit `feat: persist draws and predictions`.

### Task 3: Source downloader and update service
**Files:** Create `src/data_source.py`, `src/update_service.py`, `tests/test_update_service.py`.

**Interfaces:** `fetch_html(url, timeout=15) -> str`; `update_history(repository, start_day, days, fetcher=fetch_html) -> UpdateReport`.

- [ ] Write tests with deterministic fake fetchers for success, timeout, malformed page and partial update.
- [ ] Run tests and confirm RED.
- [ ] Implement request headers, timeout/error translation, per-day update, and `UpdateReport(success, skipped, failed, errors)`.
- [ ] Verify malformed/failed pages are not saved and previous valid data remains.
- [ ] Commit `feat: add resilient history updater`.

### Task 4: Statistical ranking engine
**Files:** Create `src/analytics.py`, `tests/test_analytics.py`.

**Interfaces:** `rank_numbers(draws) -> list[NumberScore]`; each result contains number, score, f7/f14/f30/f60/f90, gap, reverse14.

- [ ] Write tests for 100 unique outputs, descending deterministic order, capped gap signal and reverse signal.
- [ ] Run tests and confirm RED.
- [ ] Implement V1.1 weighted frequency windows `7/14/30/60/90 = .30/.24/.20/.14/.12`, capped gap contribution and capped reverse contribution.
- [ ] Normalize to 0–100 and tie-break by two-digit number.
- [ ] Run analytics tests and confirm GREEN.
- [ ] Commit `feat: add deterministic 00-99 ranking`.

### Task 5: Leak-free walk-forward backtest
**Files:** Create `src/backtest.py`, `tests/test_backtest.py`.

**Interfaces:** `walk_forward(draws, top_n, warmup=60) -> BacktestResult`.

- [ ] Write a synthetic-history test where future data would alter earlier rankings, proving only `draws[:i]` is supplied to each prediction.
- [ ] Run tests and confirm RED.
- [ ] Implement Top 1/5/10 hit-day evaluation with days, hit_days and hit_rate.
- [ ] Run backtest tests and full test suite.
- [ ] Commit `feat: add walk-forward backtest`.

### Task 6: Application service and data-directory behavior
**Files:** Create `src/app_service.py`, `src/paths.py`, `tests/test_app_service.py`.

**Interfaces:** `get_data_dir() -> Path`; `AppService.update(days)`, `AppService.analyze()`, `AppService.backtests()`.

- [ ] Write tests overriding LOCALAPPDATA to prove DB/log paths are outside the executable directory and stable across launches.
- [ ] Run tests and confirm RED.
- [ ] Implement application data directory and service orchestration.
- [ ] Verify predictions can be stored without modifying program files.
- [ ] Commit `feat: add application service`.

### Task 7: Native Windows desktop UI
**Files:** Create `src/ui.py`, `src/main.py`, `tests/test_ui_viewmodel.py`.

**Interfaces:** UI consumes only `AppService`; background worker posts completion/error back to Tk main thread.

- [ ] Write view-model formatting tests for Top 10, radar cells, backtest labels and Vietnamese error messages.
- [ ] Run tests and confirm RED.
- [ ] Implement ttk tabs: `Tổng quan`, `Radar 00–99`, `Chi tiết`, `Backtest`, `Cài đặt`.
- [ ] Add `Cập nhật dữ liệu` and `Phân tích ngày mai`; disable conflicting actions during background update.
- [ ] Display offline, timeout, changed-source-format and DB errors in-app.
- [ ] Run full tests and manually launch `python -m src.main`.
- [ ] Commit `feat: add native Windows dashboard`.

### Task 8: Packaging and release verification
**Files:** Create `XSMB_AI_Indicator.spec`, `build_windows.ps1`, `requirements-dev.txt`, `README.txt`, `tests/test_smoke.py`; remove Flask from runtime requirements.

**Interfaces:** Build output `dist/XSMB_AI_Indicator.exe`.

- [ ] Add smoke test importing `src.main` and constructing application services without network access.
- [ ] Run full tests and confirm GREEN.
- [ ] Add pinned development dependencies for pytest/PyInstaller and PyInstaller one-file/windowed configuration.
- [ ] Build on Windows with `powershell -ExecutionPolicy Bypass -File build_windows.ps1`.
- [ ] Launch `dist/XSMB_AI_Indicator.exe`, verify the window opens, `%LOCALAPPDATA%/XSMB_AI_Indicator` is created, and closing/reopening preserves data.
- [ ] Test network-disabled update and malformed fixture paths; verify visible errors and no DB corruption.
- [ ] Package EXE plus README into `XSMB_AI_Indicator_Windows.zip`.
- [ ] Commit `build: package Windows XSMB AI Indicator`.
