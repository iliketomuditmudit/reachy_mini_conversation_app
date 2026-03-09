"""Logs conversation turns to files for later analysis or use as model context.

Each session produces two files in ``conversation_logs/`` (next to CWD):

* ``conversation_<timestamp>.jsonl``  — one JSON object per line, machine-readable
* ``conversation_<timestamp>.txt``    — human-readable transcript, easy to copy-paste
  into a model as context.

Example JSONL entry::

    {"timestamp": "2026-01-15T14:32:01.123456", "role": "user", "content": "Hello!"}
    {"timestamp": "2026-01-15T14:32:02.456789", "role": "assistant", "content": "Hi there!"}
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ConversationLogger:
    """Writes each conversation turn to a JSONL log and a human-readable text file.

    Usage::

        conv_log = ConversationLogger()
        conv_log.log("user", "Hello, robot!")
        conv_log.log("assistant", "Hello! How can I help?")
        conv_log.log("tool", '{"ok": true}', metadata={"tool_name": "camera"})
        conv_log.close()

    Call ``new_session()`` when the realtime session restarts so each visitor's
    conversation is kept in a separate file.
    """

    def __init__(self, log_dir: Optional[str | Path] = None) -> None:
        self._log_dir = Path(log_dir) if log_dir else Path.cwd() / "conversation_logs"
        self._session_start = datetime.now()
        self._session_id = self._session_start.strftime("%Y%m%d_%H%M%S")
        self._jsonl_file = None
        self._txt_file = None
        self._jsonl_path: Optional[Path] = None
        self._txt_path: Optional[Path] = None
        self._setup()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _setup(self) -> None:
        """Create log directory and open log files for this session."""
        try:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            self._jsonl_path = self._log_dir / f"conversation_{self._session_id}.jsonl"
            self._txt_path = self._log_dir / f"conversation_{self._session_id}.txt"
            self._jsonl_file = open(self._jsonl_path, "a", encoding="utf-8")
            self._txt_file = open(self._txt_path, "a", encoding="utf-8")
            header = f"=== Conversation Session {self._session_id} ===\n"
            self._txt_file.write(f"{header}\n")
            self._txt_file.flush()
            logger.info("Conversation logging → %s", self._log_dir)
        except Exception as e:
            logger.warning("Could not open conversation log files: %s", e)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log(self, role: str, content: str, metadata: Optional[dict] = None) -> None:
        """Append a single turn to both log files.

        Args:
            role:     ``"user"``, ``"assistant"``, or ``"tool"``.
            content:  The text content of the turn.
            metadata: Optional dict with extra info (e.g. ``{"tool_name": "camera"}``).
        """
        if not content or not isinstance(content, str) or not content.strip():
            return

        ts = datetime.now().isoformat()
        entry: dict = {"timestamp": ts, "role": role, "content": content}
        if metadata:
            entry["metadata"] = metadata

        # --- JSONL ---
        if self._jsonl_file:
            try:
                self._jsonl_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
                self._jsonl_file.flush()
            except Exception as e:
                logger.warning("JSONL write failed: %s", e)

        # --- Human-readable text ---
        if self._txt_file:
            try:
                time_str = datetime.fromisoformat(ts).strftime("%H:%M:%S")
                _labels = {
                    "user": "👤 User",
                    "assistant": "🤖 Assistant",
                    "tool": "🛠️  Tool",
                }
                label = _labels.get(role, role.upper())
                if metadata and "tool_name" in metadata:
                    label = f"🛠️  Tool [{metadata['tool_name']}]"
                self._txt_file.write(f"[{time_str}] {label}:\n{content}\n\n")
                self._txt_file.flush()
            except Exception as e:
                logger.warning("Text log write failed: %s", e)

    def new_session(self, session_label: Optional[str] = None) -> None:
        """Close the current files and start a fresh session log.

        Call this when the realtime session restarts (e.g., for a new visitor).
        """
        self.close()
        self._session_start = datetime.now()
        self._session_id = self._session_start.strftime("%Y%m%d_%H%M%S")
        if session_label:
            self._session_id = f"{self._session_id}_{session_label}"
        self._setup()

    def close(self) -> None:
        """Flush and close file handles."""
        for f in (self._jsonl_file, self._txt_file):
            if f:
                try:
                    f.close()
                except Exception:
                    pass
        self._jsonl_file = None
        self._txt_file = None
