
#!/usr/bin/env python3
"""Collect TFA COSY BARO measurements from tfrec."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TFREC_PATH = BASE_DIR / "tfrec"
OUTPUT_PATH = BASE_DIR / "cosy_baro_latest.json"


def main():
    command = [
        str(TFREC_PATH),
        "-T", "20",
        "-J",
        "-w", "0",
    ]

    print("Starting COSY BARO collector...", file=sys.stderr)

    with subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=None,
        text=True,
        bufsize=1,
    ) as process:
        for line in process.stdout:
            try:
                measurement = json.loads(line)
            except json.JSONDecodeError:
                print(f"Ignoring invalid JSON: {line.strip()}", file=sys.stderr)
                continue

            if measurement.get("sensor") != "TFA COSY BARO":
                continue

            measurement["received_at"] = datetime.now().astimezone().isoformat(
                timespec="seconds"
            )

            temporary_path = OUTPUT_PATH.with_suffix(".json.tmp")
            temporary_path.write_text(
                json.dumps(measurement, indent=2) + "\n",
                encoding="utf-8",
            )
            temporary_path.replace(OUTPUT_PATH)

            print(
                f"Saved measurement: {measurement['temperature_c']} °C, "
                f"{measurement['humidity_percent']} %, "
                f"{measurement['pressure_hpa']} hPa",
                flush=True,
            )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCollector stopped.", file=sys.stderr)
