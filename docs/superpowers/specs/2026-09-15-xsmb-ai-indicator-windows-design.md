# XSMB AI Indicator Windows — Design Specification

## Goal
Build a self-contained Windows desktop application named `XSMB_AI_Indicator.exe` that requires no Python installation, no `.bat` launcher, and no browser/localhost workflow.

## User workflow
1. Double-click `XSMB_AI_Indicator.exe`.
2. The desktop dashboard opens directly.
3. Click **Cập nhật dữ liệu** to download and validate historical XSMB results.
4. Click **Phân tích ngày mai** to rank numbers 00–99.
5. Review Top 1/5/10, bạch thủ/song thủ, heatmap, frequency/gan/reverse indicators and backtest.
6. Predictions and subsequent actual outcomes are persisted for later evaluation.

## Architecture
- Python 3 application packaged for Windows with PyInstaller.
- Native desktop UI using Tkinter/ttk to avoid a local Flask server and browser dependency.
- SQLite local database stored under `%LOCALAPPDATA%/XSMB_AI_Indicator/`.
- Network/data-source module isolated from parser and analytics modules.
- Analytics engine treats `AI Score` only as a normalized statistical ranking score, never as a guaranteed probability.
- Build produces a single Windows executable plus optional portable ZIP.

## Components
### `src/data_source.py`
Downloads XSMB pages with timeout, user-agent, retry and explicit error messages.

### `src/parser.py`
Parses a draw into date, special prize and 27 two-digit loto values. A page is accepted only after structural validation.

### `src/storage.py`
Creates/migrates SQLite tables for draws, predictions and settings. Data lives outside the executable so upgrading the EXE does not erase history.

### `src/analytics.py`
Ranks 00–99 using frequency windows, recency/gap and reverse-number signals. Each component is separately inspectable.

### `src/backtest.py`
Walk-forward evaluation: every historical prediction uses only data available before the target draw. Reports Top 1, Top 5 and Top 10 hit-day rates and sample size.

### `src/ui.py`
Desktop dashboard with tabs: Dashboard, Radar 00–99, Chi tiết, Backtest, Cài đặt. Network work runs off the UI thread and status/errors are displayed in-app.

### `src/main.py`
Application entry point and global exception handling.

## Data integrity
- Never silently treat a malformed page as a valid draw.
- Reject a parsed draw unless the date is valid and the expected prize/result structure is present.
- Store source URL and fetch timestamp with each draw.
- Existing valid rows are preserved when an update fails.
- Update status reports successful, skipped and failed dates.

## Analytics V1.1
The initial score preserves the V1 concept but makes it testable:
- Frequency: 7, 14, 30, 60, 90 draws.
- Gap/recency signal is capped.
- Reverse-number signal is capped.
- Normalize final ranking to 0–100.
- Stable deterministic tie-breaking by number.
- UI labels the metric `AI Score (điểm thống kê)`.

No claim is made that a high score changes the true lottery probability.

## Backtesting
- Minimum warm-up before evaluation.
- No future-data leakage.
- Report exact evaluated days and hit days.
- Persist daily predictions so real forward performance can be compared with historical backtest.
- Future model optimization must use train/validation separation rather than optimizing and reporting on the same period.

## Error handling
- Offline: show `Không có kết nối mạng`.
- Source timeout: show timeout and allow retry.
- HTML/source format changed: show `Không đọc được cấu trúc dữ liệu nguồn`; do not save corrupted data.
- Database error: show readable message and log technical detail.
- Unexpected exception: write a log under the application data directory and keep the UI from failing silently.

## Windows packaging
- PyInstaller one-file/windowed executable.
- Runtime data path resolved independently of the EXE directory.
- No console window required for normal use.
- Build script creates `dist/XSMB_AI_Indicator.exe`.
- Smoke test launches the packaged EXE and verifies the database directory can be created.

## Tests
Automated tests cover:
- Known HTML fixture parsing.
- Malformed HTML rejection.
- Score determinism and 00–99 completeness.
- Gap/reverse calculations.
- Walk-forward no-lookahead behavior.
- SQLite persistence and migration.
- Network failure handling with controlled test doubles.
- App startup/service wiring.

## Acceptance criteria
- Runs on supported 64-bit Windows by double-clicking one `.exe`.
- Does not require Python, pip, Flask, `.bat`, or a browser.
- Can update data, analyze 00–99 and show backtest from the desktop UI.
- A network/source failure produces a visible error and does not corrupt stored history.
- User data survives replacement of the EXE with a newer build.
- All automated tests pass before release.
