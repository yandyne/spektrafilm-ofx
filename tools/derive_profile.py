"""Create a stock profile that reuses another stock's measured data.

Used for films that are known to be an existing emulsion in a different package
(rem-jet removed Vision3, re-branded Gold 200, ...). Copies the release, archive and
Python package profiles plus the neutral print filter entries, changes only the
fields given, and records the derivation in the profile metadata as the CC BY-SA
licence of the source profiles asks for ("Modifications must be noted").

Usage:
  python derive_profile.py NEW_STOCK BASE_STOCK "Display Name" "note" [info_key=value ...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OFX = ROOT / "build/ofx/SpektraFilm/Resources/data"
PY = ROOT / "references/spektrafilm-main/src/spektrafilm/data"
PROFILE_DIRS = [OFX / "profiles", OFX / "profiles/archive", PY / "profiles"]
FILTER_FILES = [OFX / "filters/neutral_print_filters.json", PY / "filters/neutral_print_filters.json"]


def derive(stock: str, base: str, name: str, note: str, info: dict[str, str]) -> None:
    for d in PROFILE_DIRS:
        p = json.loads((d / f"{base}.json").read_text())
        p["info"].update(stock=stock, name=name, **info)
        p.setdefault("metadata", {})["derivation"] = f"Derived by PhotoEmul from {base}: {note}"
        (d / f"{stock}.json").write_text(json.dumps(p, indent=4))
    for f in FILTER_FILES:
        filters = json.loads(f.read_text())
        for paper in filters.values():
            for table in paper.values():
                if base in table:
                    table[stock] = table[base]
        f.write_text(json.dumps(filters, indent=4))


if __name__ == "__main__":
    stock, base, name, note, *extra = sys.argv[1:]
    derive(stock, base, name, note, dict(kv.split("=", 1) for kv in extra))
