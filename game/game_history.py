import json
from datetime import datetime, timezone
from pathlib import Path


class GameHistoryStore:
    HISTORY_FILE = Path.home() / ".chessvar" / "game_history.json"

    @classmethod
    def load(cls):
        if not cls.HISTORY_FILE.exists():
            return []
        try:
            with cls.HISTORY_FILE.open("r", encoding="utf-8") as history_file:
                payload = json.load(history_file)
        except (OSError, json.JSONDecodeError):
            return []

        entries = payload.get("entries", [])
        if not isinstance(entries, list):
            return []
        return entries

    @classmethod
    def add_entry(cls, *, variant, mode, result_type, winner, reason, move_count):
        entries = cls.load()
        entries.insert(
            0,
            {
                "played_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "variant": variant,
                "mode": mode,
                "result_type": result_type,
                "winner": winner,
                "reason": reason,
                "move_count": move_count,
            },
        )
        cls._save(entries)

    @classmethod
    def _save(cls, entries):
        try:
            cls.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with cls.HISTORY_FILE.open("w", encoding="utf-8") as history_file:
                json.dump({"entries": entries[:200]}, history_file, indent=2)
        except OSError:
            pass