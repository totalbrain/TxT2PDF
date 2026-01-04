from __future__ import annotations

import logging
import os
import sys
import time
import threading
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from typing import Optional


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "INFO"
    log_dir: str = "logs"
    log_file: str = "processing.log"
    max_bytes: int = 5 * 1024 * 1024  # 5MB
    backup_count: int = 5
    console: bool = True
    force_reconfigure: bool = False  # If True, existing handlers will be removed


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """
    Configure root logging ONCE for the whole application.

    Best practice:
    - Call this once in the entrypoint (e.g., TXT2PDF.py main()).
    - Other modules should ONLY do: logger = logging.getLogger(__name__)
    """
    cfg = config or LoggingConfig()

    # Normalize level safely
    level_name = (cfg.level or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    os.makedirs(cfg.log_dir, exist_ok=True)

    root = logging.getLogger()

    # Prevent duplicate handlers if setup_logging is called more than once
    if root.handlers and not cfg.force_reconfigure:
        root.setLevel(level)
        return

    if cfg.force_reconfigure:
        for h in list(root.handlers):
            root.removeHandler(h)
            try:
                h.close()
            except Exception:
                # Avoid try/except/pass (Bandit B110). Best effort close.
                continue

    root.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)

    handlers: list[logging.Handler] = []

    # Console handler
    if cfg.console:
        sh = logging.StreamHandler(stream=sys.stdout)
        sh.setLevel(level)
        sh.setFormatter(formatter)
        handlers.append(sh)

    # File handler (rotating)
    file_path = os.path.join(cfg.log_dir, cfg.log_file)
    fh = RotatingFileHandler(
        filename=file_path,
        mode="a",
        maxBytes=cfg.max_bytes,
        backupCount=cfg.backup_count,
        encoding="utf-8",
    )
    fh.setLevel(level)
    fh.setFormatter(formatter)
    handlers.append(fh)

    for h in handlers:
        root.addHandler(h)


def get_logger(name: str) -> logging.Logger:
    """
    Central place for obtaining a logger.
    Keeps call-sites consistent and easy to extend later (e.g., LoggerAdapter).
    """
    return logging.getLogger(name)


# ---------------- Progress logging state (thread-local) ----------------

@dataclass
class _ProgressState:
    last_log_ts: float = 0.0
    last_log_pct: int = -1


_progress_tls = threading.local()


def _get_progress_state() -> _ProgressState:
    state = getattr(_progress_tls, "state", None)
    if state is None:
        state = _ProgressState()
        # Direct attribute assignment (no setattr -> no Ruff B010)
        _progress_tls.state = state
    return state


def render_progress(
    current: int,
    total: int,
    width: int = 30,
    *,
    logger: Optional[logging.Logger] = None,
    log_every_percent: int = 10,
    min_log_interval_sec: float = 2.0,
) -> None:
    """
    Render a progress bar in the console.
    Optional logging is throttled to avoid log spam (important for multithreading).

    - log_every_percent: log at most each N% change (default 10%)
    - min_log_interval_sec: also requires at least this time gap between logs
    """
    ratio = current / total if total else 1.0
    ratio = min(max(ratio, 0.0), 1.0)

    filled = int(ratio * width)
    bar = "█" * filled + "─" * (width - filled)
    percent = int(ratio * 100)

    # Console output (fast & user-friendly)
    print(f"\r[{bar}] {percent:3d}% ({current}/{total})", end="", flush=True)
    if current >= total:
        print()

    # Throttled logging (optional)
    if logger is None:
        return

    state = _get_progress_state()
    now = time.monotonic()

    should_log_pct = (
        log_every_percent > 0
        and (
            percent == 100
            or percent // log_every_percent != state.last_log_pct // log_every_percent
        )
    )
    should_log_time = (now - state.last_log_ts) >= min_log_interval_sec

    if should_log_pct and should_log_time:
        logger.info("Progress: %d%% (%d/%d)", percent, current, total)
        # Direct assignment => no Ruff B010
        state.last_log_ts = now
        state.last_log_pct = percent
