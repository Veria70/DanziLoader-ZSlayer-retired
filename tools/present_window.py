"""Summarize consecutive VIctory diagnostic present events (Python 3.11+)."""
import argparse
from datetime import datetime
import json
from math import ceil
from pathlib import Path
import re
from statistics import median

ANSI = re.compile(r"\x1b\[[\d;]*m")
PRESENT = re.compile(r"^(\S+Z) DEBUG victory_gpu::frame: present token=(\d+)\b")


def measure(path, start, count):
    if start < 0 or count < 1:
        raise ValueError("start must be nonnegative and count must be positive")
    times = []
    with path.open(encoding="utf-8", errors="replace") as source:
        for line in source:
            event = PRESENT.search(ANSI.sub("", line))
            if not event:
                continue
            token = int(event[2])
            if not start <= token <= start + count:
                continue
            if token != start + len(times):
                raise ValueError(f"Missing or repeated present near token {token}")
            times.append(datetime.fromisoformat(event[1]))
    if len(times) != count + 1:
        raise ValueError("The log does not contain the full requested window")
    ms = [(b - a).total_seconds() * 1000 for a, b in zip(times, times[1:])]
    if min(ms) <= 0:
        raise ValueError("Timestamps must strictly increase")
    return {
        "first_token": start, "frames": count, "fps": 1000 * count / sum(ms),
        "median_ms": median(ms), "p95_ms": sorted(ms)[ceil(count * .95) - 1],
        "within_40_ms": sum(frame <= 40 for frame in ms),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("first_token", type=int)
    parser.add_argument("--frames", type=int, default=240)
    args = parser.parse_args()
    print(json.dumps(measure(args.log, args.first_token, args.frames), indent=2))
